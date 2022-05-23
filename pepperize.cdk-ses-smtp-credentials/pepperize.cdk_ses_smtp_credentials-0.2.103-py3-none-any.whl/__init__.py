'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-ses-smtp-credentials?style=flat-square)](https://github.com/pepperize/cdk-ses-smtp-credentials/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-ses-smtp-credentials?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-ses-smtp-credentials)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-ses-smtp-credentials?style=flat-square)](https://pypi.org/project/pepperize.cdk-ses-smtp-credentials/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.SesSmtpCredentials?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.SesSmtpCredentials/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-ses-smtp-credentials/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-ses-smtp-credentials/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-ses-smtp-credentials?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-ses-smtp-credentials/releases)

# AWS CDK Ses Smtp Credentials

This projects provides a CDK construct to create ses smtp credentials for a given user. It takes a username, creates an AccessKey and generates the smtp password.

## Install

### TypeScript

```shell
npm install @pepperize/cdk-ses-smtp-credentials
```

or

```shell
yarn add @pepperize/cdk-ses-smtp-credentials
```

### Python

```shell
pip install pepperize.cdk-ses-smtp-credentials
```

### C# / .Net

```
dotnet add package Pepperize.CDK.SesSmtpCredentials
```

## Example

```shell
npm install @pepperize/cdk-ses-smtp-credentials
```

See [API.md](https://github.com/pepperize/cdk-ses-smtp-credentials/blob/main/API.md).

```python
import { User } from "@aws-cdk/aws-iam";
import { SesSmtpCredentials } from "@pepperize/cdk-ses-smtp-credentials";

const username = "ses-user";
const user = new User(stack, "SesUser", {
  userName: username,
});
const smtpCredentials = new SesSmtpCredentials(this, "SmtpCredentials", {
  user: user,
});

// smtpCredentials.secret contains json value {username: "<the generated access key id>", password: "<the calculated ses smtp password>"}
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
import aws_cdk.aws_codeguruprofiler
import aws_cdk.aws_ec2
import aws_cdk.aws_iam
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_sqs
import constructs


@jsii.enum(jsii_type="@pepperize/cdk-ses-smtp-credentials.Credentials")
class Credentials(enum.Enum):
    USERNAME = "USERNAME"
    '''The key of the username stored in the secretsmanager key/value json text.'''
    PASSWORD = "PASSWORD"
    '''The key of the password stored in the secretsmanager key/value json.'''


class CredentialsHandlerFunction(
    aws_cdk.aws_lambda.Function,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-ses-smtp-credentials.CredentialsHandlerFunction",
):
    '''An AWS Lambda function which executes src/provider/credentials-handler.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        code_signing_config: typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[aws_cdk.aws_lambda.VersionOptions] = None,
        dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        events: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.IEventSource]] = None,
        filesystem: typing.Optional[aws_cdk.aws_lambda.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        insights_version: typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions] = None,
        log_retention_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        tracing: typing.Optional[aws_cdk.aws_lambda.Tracing] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        max_event_age: typing.Optional[aws_cdk.Duration] = None,
        on_failure: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_success: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - the Vpc default strategy if not specified
        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        '''
        props = CredentialsHandlerFunctionProps(
            allow_all_outbound=allow_all_outbound,
            allow_public_subnet=allow_public_subnet,
            architecture=architecture,
            code_signing_config=code_signing_config,
            current_version_options=current_version_options,
            dead_letter_queue=dead_letter_queue,
            dead_letter_queue_enabled=dead_letter_queue_enabled,
            description=description,
            environment=environment,
            environment_encryption=environment_encryption,
            events=events,
            filesystem=filesystem,
            function_name=function_name,
            initial_policy=initial_policy,
            insights_version=insights_version,
            layers=layers,
            log_retention=log_retention,
            log_retention_retry_options=log_retention_retry_options,
            log_retention_role=log_retention_role,
            memory_size=memory_size,
            profiling=profiling,
            profiling_group=profiling_group,
            reserved_concurrent_executions=reserved_concurrent_executions,
            role=role,
            security_groups=security_groups,
            timeout=timeout,
            tracing=tracing,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            max_event_age=max_event_age,
            on_failure=on_failure,
            on_success=on_success,
            retry_attempts=retry_attempts,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-ses-smtp-credentials.CredentialsHandlerFunctionProps",
    jsii_struct_bases=[aws_cdk.aws_lambda.FunctionOptions],
    name_mapping={
        "max_event_age": "maxEventAge",
        "on_failure": "onFailure",
        "on_success": "onSuccess",
        "retry_attempts": "retryAttempts",
        "allow_all_outbound": "allowAllOutbound",
        "allow_public_subnet": "allowPublicSubnet",
        "architecture": "architecture",
        "code_signing_config": "codeSigningConfig",
        "current_version_options": "currentVersionOptions",
        "dead_letter_queue": "deadLetterQueue",
        "dead_letter_queue_enabled": "deadLetterQueueEnabled",
        "description": "description",
        "environment": "environment",
        "environment_encryption": "environmentEncryption",
        "events": "events",
        "filesystem": "filesystem",
        "function_name": "functionName",
        "initial_policy": "initialPolicy",
        "insights_version": "insightsVersion",
        "layers": "layers",
        "log_retention": "logRetention",
        "log_retention_retry_options": "logRetentionRetryOptions",
        "log_retention_role": "logRetentionRole",
        "memory_size": "memorySize",
        "profiling": "profiling",
        "profiling_group": "profilingGroup",
        "reserved_concurrent_executions": "reservedConcurrentExecutions",
        "role": "role",
        "security_groups": "securityGroups",
        "timeout": "timeout",
        "tracing": "tracing",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
    },
)
class CredentialsHandlerFunctionProps(aws_cdk.aws_lambda.FunctionOptions):
    def __init__(
        self,
        *,
        max_event_age: typing.Optional[aws_cdk.Duration] = None,
        on_failure: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        on_success: typing.Optional[aws_cdk.aws_lambda.IDestination] = None,
        retry_attempts: typing.Optional[jsii.Number] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        allow_public_subnet: typing.Optional[builtins.bool] = None,
        architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        code_signing_config: typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig] = None,
        current_version_options: typing.Optional[aws_cdk.aws_lambda.VersionOptions] = None,
        dead_letter_queue: typing.Optional[aws_cdk.aws_sqs.IQueue] = None,
        dead_letter_queue_enabled: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        environment_encryption: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        events: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.IEventSource]] = None,
        filesystem: typing.Optional[aws_cdk.aws_lambda.FileSystem] = None,
        function_name: typing.Optional[builtins.str] = None,
        initial_policy: typing.Optional[typing.Sequence[aws_cdk.aws_iam.PolicyStatement]] = None,
        insights_version: typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion] = None,
        layers: typing.Optional[typing.Sequence[aws_cdk.aws_lambda.ILayerVersion]] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        log_retention_retry_options: typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions] = None,
        log_retention_role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        profiling: typing.Optional[builtins.bool] = None,
        profiling_group: typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup] = None,
        reserved_concurrent_executions: typing.Optional[jsii.Number] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[aws_cdk.aws_ec2.ISecurityGroup]] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        tracing: typing.Optional[aws_cdk.aws_lambda.Tracing] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        vpc_subnets: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''Props for CredentialsHandlerFunction.

        :param max_event_age: The maximum age of a request that Lambda sends to a function for processing. Minimum: 60 seconds Maximum: 6 hours Default: Duration.hours(6)
        :param on_failure: The destination for failed invocations. Default: - no destination
        :param on_success: The destination for successful invocations. Default: - no destination
        :param retry_attempts: The maximum number of times to retry when the function returns an error. Minimum: 0 Maximum: 2 Default: 2
        :param allow_all_outbound: Whether to allow the Lambda to send all network traffic. If set to false, you must individually add traffic rules to allow the Lambda to connect to network targets. Default: true
        :param allow_public_subnet: Lambda Functions in a public subnet can NOT access the internet. Use this property to acknowledge this limitation and still place the function in a public subnet. Default: false
        :param architecture: The system architectures compatible with this lambda function. Default: Architecture.X86_64
        :param code_signing_config: Code signing config associated with this function. Default: - Not Sign the Code
        :param current_version_options: Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method. Default: - default options as described in ``VersionOptions``
        :param dead_letter_queue: The SQS queue to use if DLQ is enabled. Default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        :param dead_letter_queue_enabled: Enabled DLQ. If ``deadLetterQueue`` is undefined, an SQS queue with default options will be defined for your Function. Default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        :param description: A description of the function. Default: - No description.
        :param environment: Key-value pairs that Lambda caches and makes available for your Lambda functions. Use environment variables to apply configuration changes, such as test and production environment configurations, without changing your Lambda function source code. Default: - No environment variables.
        :param environment_encryption: The AWS KMS key that's used to encrypt your function's environment variables. Default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        :param events: Event sources for this function. You can also add event sources using ``addEventSource``. Default: - No event sources.
        :param filesystem: The filesystem configuration for the lambda function. Default: - will not mount any filesystem
        :param function_name: A name for the function. Default: - AWS CloudFormation generates a unique physical ID and uses that ID for the function's name. For more information, see Name Type.
        :param initial_policy: Initial policy statements to add to the created Lambda Role. You can call ``addToRolePolicy`` to the created lambda to add statements post creation. Default: - No policy statements are added to the created Lambda role.
        :param insights_version: Specify the version of CloudWatch Lambda insights to use for monitoring. Default: - No Lambda Insights
        :param layers: A list of layers to add to the function's execution environment. You can configure your Lambda function to pull in additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies that can be used by multiple functions. Default: - No layers.
        :param log_retention: The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.INFINITE
        :param log_retention_retry_options: When log retention is specified, a custom resource attempts to create the CloudWatch log group. These options control the retry policy when interacting with CloudWatch APIs. Default: - Default AWS SDK retry options.
        :param log_retention_role: The IAM role for the Lambda function associated with the custom resource that sets the retention policy. Default: - A new role is created.
        :param memory_size: The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 128
        :param profiling: Enable profiling. Default: - No profiling.
        :param profiling_group: Profiling Group. Default: - A new profiling group will be created if ``profiling`` is set.
        :param reserved_concurrent_executions: The maximum of concurrent executions you want to reserve for the function. Default: - No specific limit - account limit.
        :param role: Lambda execution role. This is the role that will be assumed by the function upon execution. It controls the permissions that the function will have. The Role must be assumable by the 'lambda.amazonaws.com' service principal. The default Role automatically has permissions granted for Lambda execution. If you provide a Role, you must add the relevant AWS managed policies yourself. The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and "service-role/AWSLambdaVPCAccessExecutionRole". Default: - A unique role will be generated for this lambda function. Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        :param security_groups: The list of security groups to associate with the Lambda's network interfaces. Only used if 'vpc' is supplied. Default: - If the function is placed within a VPC and a security group is not specified, either by this or securityGroup prop, a dedicated security group will be created for this function.
        :param timeout: The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.seconds(3)
        :param tracing: Enable AWS X-Ray Tracing for Lambda Function. Default: Tracing.Disabled
        :param vpc: VPC network to place Lambda network interfaces. Specify this if the Lambda function needs to access resources in a VPC. Default: - Function is not placed within a VPC.
        :param vpc_subnets: Where to place the network interfaces within the VPC. Only used if 'vpc' is supplied. Note: internet access for Lambdas requires a NAT gateway, so picking Public subnets is not allowed. Default: - the Vpc default strategy if not specified
        '''
        if isinstance(current_version_options, dict):
            current_version_options = aws_cdk.aws_lambda.VersionOptions(**current_version_options)
        if isinstance(log_retention_retry_options, dict):
            log_retention_retry_options = aws_cdk.aws_lambda.LogRetentionRetryOptions(**log_retention_retry_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = aws_cdk.aws_ec2.SubnetSelection(**vpc_subnets)
        self._values: typing.Dict[str, typing.Any] = {}
        if max_event_age is not None:
            self._values["max_event_age"] = max_event_age
        if on_failure is not None:
            self._values["on_failure"] = on_failure
        if on_success is not None:
            self._values["on_success"] = on_success
        if retry_attempts is not None:
            self._values["retry_attempts"] = retry_attempts
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if allow_public_subnet is not None:
            self._values["allow_public_subnet"] = allow_public_subnet
        if architecture is not None:
            self._values["architecture"] = architecture
        if code_signing_config is not None:
            self._values["code_signing_config"] = code_signing_config
        if current_version_options is not None:
            self._values["current_version_options"] = current_version_options
        if dead_letter_queue is not None:
            self._values["dead_letter_queue"] = dead_letter_queue
        if dead_letter_queue_enabled is not None:
            self._values["dead_letter_queue_enabled"] = dead_letter_queue_enabled
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if environment_encryption is not None:
            self._values["environment_encryption"] = environment_encryption
        if events is not None:
            self._values["events"] = events
        if filesystem is not None:
            self._values["filesystem"] = filesystem
        if function_name is not None:
            self._values["function_name"] = function_name
        if initial_policy is not None:
            self._values["initial_policy"] = initial_policy
        if insights_version is not None:
            self._values["insights_version"] = insights_version
        if layers is not None:
            self._values["layers"] = layers
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if log_retention_retry_options is not None:
            self._values["log_retention_retry_options"] = log_retention_retry_options
        if log_retention_role is not None:
            self._values["log_retention_role"] = log_retention_role
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if profiling is not None:
            self._values["profiling"] = profiling
        if profiling_group is not None:
            self._values["profiling_group"] = profiling_group
        if reserved_concurrent_executions is not None:
            self._values["reserved_concurrent_executions"] = reserved_concurrent_executions
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if timeout is not None:
            self._values["timeout"] = timeout
        if tracing is not None:
            self._values["tracing"] = tracing
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def max_event_age(self) -> typing.Optional[aws_cdk.Duration]:
        '''The maximum age of a request that Lambda sends to a function for processing.

        Minimum: 60 seconds
        Maximum: 6 hours

        :default: Duration.hours(6)
        '''
        result = self._values.get("max_event_age")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def on_failure(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The destination for failed invocations.

        :default: - no destination
        '''
        result = self._values.get("on_failure")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def on_success(self) -> typing.Optional[aws_cdk.aws_lambda.IDestination]:
        '''The destination for successful invocations.

        :default: - no destination
        '''
        result = self._values.get("on_success")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.IDestination], result)

    @builtins.property
    def retry_attempts(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of times to retry when the function returns an error.

        Minimum: 0
        Maximum: 2

        :default: 2
        '''
        result = self._values.get("retry_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether to allow the Lambda to send all network traffic.

        If set to false, you must individually add traffic rules to allow the
        Lambda to connect to network targets.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_public_subnet(self) -> typing.Optional[builtins.bool]:
        '''Lambda Functions in a public subnet can NOT access the internet.

        Use this property to acknowledge this limitation and still place the function in a public subnet.

        :default: false

        :see: https://stackoverflow.com/questions/52992085/why-cant-an-aws-lambda-function-inside-a-public-subnet-in-a-vpc-connect-to-the/52994841#52994841
        '''
        result = self._values.get("allow_public_subnet")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def architecture(self) -> typing.Optional[aws_cdk.aws_lambda.Architecture]:
        '''The system architectures compatible with this lambda function.

        :default: Architecture.X86_64
        '''
        result = self._values.get("architecture")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Architecture], result)

    @builtins.property
    def code_signing_config(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig]:
        '''Code signing config associated with this function.

        :default: - Not Sign the Code
        '''
        result = self._values.get("code_signing_config")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.ICodeSigningConfig], result)

    @builtins.property
    def current_version_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.VersionOptions]:
        '''Options for the ``lambda.Version`` resource automatically created by the ``fn.currentVersion`` method.

        :default: - default options as described in ``VersionOptions``
        '''
        result = self._values.get("current_version_options")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.VersionOptions], result)

    @builtins.property
    def dead_letter_queue(self) -> typing.Optional[aws_cdk.aws_sqs.IQueue]:
        '''The SQS queue to use if DLQ is enabled.

        :default: - SQS queue with 14 day retention period if ``deadLetterQueueEnabled`` is ``true``
        '''
        result = self._values.get("dead_letter_queue")
        return typing.cast(typing.Optional[aws_cdk.aws_sqs.IQueue], result)

    @builtins.property
    def dead_letter_queue_enabled(self) -> typing.Optional[builtins.bool]:
        '''Enabled DLQ.

        If ``deadLetterQueue`` is undefined,
        an SQS queue with default options will be defined for your Function.

        :default: - false unless ``deadLetterQueue`` is set, which implies DLQ is enabled.
        '''
        result = self._values.get("dead_letter_queue_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the function.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key-value pairs that Lambda caches and makes available for your Lambda functions.

        Use environment variables to apply configuration changes, such
        as test and production environment configurations, without changing your
        Lambda function source code.

        :default: - No environment variables.
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def environment_encryption(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''The AWS KMS key that's used to encrypt your function's environment variables.

        :default: - AWS Lambda creates and uses an AWS managed customer master key (CMK).
        '''
        result = self._values.get("environment_encryption")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def events(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.IEventSource]]:
        '''Event sources for this function.

        You can also add event sources using ``addEventSource``.

        :default: - No event sources.
        '''
        result = self._values.get("events")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.IEventSource]], result)

    @builtins.property
    def filesystem(self) -> typing.Optional[aws_cdk.aws_lambda.FileSystem]:
        '''The filesystem configuration for the lambda function.

        :default: - will not mount any filesystem
        '''
        result = self._values.get("filesystem")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.FileSystem], result)

    @builtins.property
    def function_name(self) -> typing.Optional[builtins.str]:
        '''A name for the function.

        :default:

        - AWS CloudFormation generates a unique physical ID and uses that
        ID for the function's name. For more information, see Name Type.
        '''
        result = self._values.get("function_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def initial_policy(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]]:
        '''Initial policy statements to add to the created Lambda Role.

        You can call ``addToRolePolicy`` to the created lambda to add statements post creation.

        :default: - No policy statements are added to the created Lambda role.
        '''
        result = self._values.get("initial_policy")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.PolicyStatement]], result)

    @builtins.property
    def insights_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion]:
        '''Specify the version of CloudWatch Lambda insights to use for monitoring.

        :default: - No Lambda Insights

        :see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Lambda-Insights-Getting-Started-docker.html
        '''
        result = self._values.get("insights_version")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.LambdaInsightsVersion], result)

    @builtins.property
    def layers(self) -> typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]]:
        '''A list of layers to add to the function's execution environment.

        You can configure your Lambda function to pull in
        additional code during initialization in the form of layers. Layers are packages of libraries or other dependencies
        that can be used by multiple functions.

        :default: - No layers.
        '''
        result = self._values.get("layers")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_lambda.ILayerVersion]], result)

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.INFINITE
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def log_retention_retry_options(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions]:
        '''When log retention is specified, a custom resource attempts to create the CloudWatch log group.

        These options control the retry policy when interacting with CloudWatch APIs.

        :default: - Default AWS SDK retry options.
        '''
        result = self._values.get("log_retention_retry_options")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.LogRetentionRetryOptions], result)

    @builtins.property
    def log_retention_role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''The IAM role for the Lambda function associated with the custom resource that sets the retention policy.

        :default: - A new role is created.
        '''
        result = self._values.get("log_retention_role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU
        power. For more information, see Resource Model in the AWS Lambda
        Developer Guide.

        :default: 128
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def profiling(self) -> typing.Optional[builtins.bool]:
        '''Enable profiling.

        :default: - No profiling.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def profiling_group(
        self,
    ) -> typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup]:
        '''Profiling Group.

        :default: - A new profiling group will be created if ``profiling`` is set.

        :see: https://docs.aws.amazon.com/codeguru/latest/profiler-ug/setting-up-lambda.html
        '''
        result = self._values.get("profiling_group")
        return typing.cast(typing.Optional[aws_cdk.aws_codeguruprofiler.IProfilingGroup], result)

    @builtins.property
    def reserved_concurrent_executions(self) -> typing.Optional[jsii.Number]:
        '''The maximum of concurrent executions you want to reserve for the function.

        :default: - No specific limit - account limit.

        :see: https://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html
        '''
        result = self._values.get("reserved_concurrent_executions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        '''Lambda execution role.

        This is the role that will be assumed by the function upon execution.
        It controls the permissions that the function will have. The Role must
        be assumable by the 'lambda.amazonaws.com' service principal.

        The default Role automatically has permissions granted for Lambda execution. If you
        provide a Role, you must add the relevant AWS managed policies yourself.

        The relevant managed policies are "service-role/AWSLambdaBasicExecutionRole" and
        "service-role/AWSLambdaVPCAccessExecutionRole".

        :default:

        - A unique role will be generated for this lambda function.
        Both supplied and generated roles can always be changed by calling ``addToRolePolicy``.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[aws_cdk.aws_iam.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]]:
        '''The list of security groups to associate with the Lambda's network interfaces.

        Only used if 'vpc' is supplied.

        :default:

        - If the function is placed within a VPC and a security group is
        not specified, either by this or securityGroup prop, a dedicated security
        group will be created for this function.
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_ec2.ISecurityGroup]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.seconds(3)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def tracing(self) -> typing.Optional[aws_cdk.aws_lambda.Tracing]:
        '''Enable AWS X-Ray Tracing for Lambda Function.

        :default: Tracing.Disabled
        '''
        result = self._values.get("tracing")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Tracing], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''VPC network to place Lambda network interfaces.

        Specify this if the Lambda function needs to access resources in a VPC.

        :default: - Function is not placed within a VPC.
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where to place the network interfaces within the VPC.

        Only used if 'vpc' is supplied. Note: internet access for Lambdas
        requires a NAT gateway, so picking Public subnets is not allowed.

        :default: - the Vpc default strategy if not specified
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CredentialsHandlerFunctionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CredentialsProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-ses-smtp-credentials.CredentialsProvider",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret: aws_cdk.aws_secretsmanager.ISecret,
        user: aws_cdk.aws_iam.IUser,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: 
        :param user: 
        '''
        props = SesSmtpCredentialsProviderProps(secret=secret, user=user)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))


class SesSmtpCredentials(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-ses-smtp-credentials.SesSmtpCredentials",
):
    '''This construct creates an access key for the given user and stores the generated SMTP credentials inside a secret.

    Example::

        const user = User.fromUserName("ses-user-example");
        const credentials = new SesSmtpCredentials(this, 'SmtpCredentials', {
            user: user,
        });
        // credentials.secret
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        user: aws_cdk.aws_iam.IUser,
        secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param user: The user for which to create an AWS Access Key and to generate the smtp password.
        :param secret: Optional, an SecretsManager secret to write the AWS SES Smtp credentials to.
        '''
        props = SesSmtpCredentialsProps(user=user, secret=secret)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "secret"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-ses-smtp-credentials.SesSmtpCredentialsProps",
    jsii_struct_bases=[],
    name_mapping={"user": "user", "secret": "secret"},
)
class SesSmtpCredentialsProps:
    def __init__(
        self,
        *,
        user: aws_cdk.aws_iam.IUser,
        secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
    ) -> None:
        '''
        :param user: The user for which to create an AWS Access Key and to generate the smtp password.
        :param secret: Optional, an SecretsManager secret to write the AWS SES Smtp credentials to.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "user": user,
        }
        if secret is not None:
            self._values["secret"] = secret

    @builtins.property
    def user(self) -> aws_cdk.aws_iam.IUser:
        '''The user for which to create an AWS Access Key and to generate the smtp password.'''
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(aws_cdk.aws_iam.IUser, result)

    @builtins.property
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''Optional, an SecretsManager secret to write the AWS SES Smtp credentials to.'''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesSmtpCredentialsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-ses-smtp-credentials.SesSmtpCredentialsProviderProps",
    jsii_struct_bases=[],
    name_mapping={"secret": "secret", "user": "user"},
)
class SesSmtpCredentialsProviderProps:
    def __init__(
        self,
        *,
        secret: aws_cdk.aws_secretsmanager.ISecret,
        user: aws_cdk.aws_iam.IUser,
    ) -> None:
        '''
        :param secret: 
        :param user: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "secret": secret,
            "user": user,
        }

    @builtins.property
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    @builtins.property
    def user(self) -> aws_cdk.aws_iam.IUser:
        result = self._values.get("user")
        assert result is not None, "Required property 'user' is missing"
        return typing.cast(aws_cdk.aws_iam.IUser, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SesSmtpCredentialsProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Credentials",
    "CredentialsHandlerFunction",
    "CredentialsHandlerFunctionProps",
    "CredentialsProvider",
    "SesSmtpCredentials",
    "SesSmtpCredentialsProps",
    "SesSmtpCredentialsProviderProps",
]

publication.publish()
