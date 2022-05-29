'''
# Fantasy Hockey Notifier CDK

> AWS CDK construct to send notifications for adds, drops, and trades in an ESPN Fantasy Hockey league

[![NPM version](https://badge.fury.io/js/fantasy-hockey-notifier-cdk.svg)](https://badge.fury.io/js/fantasy-hockey-notifier-cdk)
[![PyPI version](https://badge.fury.io/py/fantasy-hockey-notifier-cdk.svg)](https://badge.fury.io/py/fantasy-hockey-notifier-cdk)
[![Release](https://github.com/ftalburt/fantasy-hockey-notifier-cdk/actions/workflows/release.yml/badge.svg)](https://github.com/ftalburt/fantasy-hockey-notifier-cdk/actions/workflows/release.yml)

This application checks for and sends notifications about adds, drops, and trades in an ESPN Fantasy Hockey league. All ESPN APIs used are unofficial and undocumented, thus this application may break at some point in the future if ESPN changes the response schema for any of the endpoints. The codebase supports local execution, along with deployment to AWS using [AWS CDK](https://aws.amazon.com/cdk).

## Local Execution

In addition to being consumable as a CDK construct (which is the primary use-case), the project supports local execution for testing purposes.

### Prerequisites for Local Execution

* Node.js 14 or later
* See the [Environment Variables](#environment-variables) section for a list of required and optional variables that should be exported in the shell or set in the .env file
* If using any of the environment variables starting with `AWS_` or ending with `_SSM`, you must configure AWS credentials via a local credentials file or environment variables. See the [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for details.

### Shell Commands for Local Execution

```sh
npm ci
npm start
```

## API Reference

See [API.md](./API.md).

## Environment Variables

### Required Variables

`FH_SEASON` or `FH_SEASON_SSM`: The year of the fantasy hockey season (i.e. `2020` for the 2019-2020 season)

`FH_LEAGUE_ID` or `FH_LEAGUE_ID_SSM`: The ID of the ESPN fantasy hockey league (this is displayed in the URL when you go to the `My Team` page) or the path for an SSM parameter with this value (SSM variable takes prescedence if both are specified)

`ESPN_S2_COOKIE` or `ESPN_S2_COOKIE_SSM`: The value of your `espn_s2` cookie to be used for authentication (you can find this by examining stored cookies for espn.com using the Chrome or Firefox developer tools) or the path for an SSM parameter with this value (SSM variable takes prescedence if both are specified)

### Optional Variables

`AWS_SNS_TOPIC_ARN`: The ARN of an existing AWS SNS topic

`AWS_DYNAMO_DB_TABLE_NAME` or `DISCORD_WEBHOOK_SSM`: The name of an existing Dynamo DB table to use for storing last run dates (takes priority over `LAST_RUN_FILE_PATH` if both are set) or the path for an SSM parameter with this value (SSM variable takes prescedence if both are specified)

`DISCORD_WEBHOOK`: A Discord webhook URL

`LAST_RUN_FILE_PATH`: A local file path to use for storing last run dates (defaults to `.lastrun`)

`EARLIEST_DATE`: A unix timestamp in milliseconds to use as the earliest date when looking up transactions

`LATEST_DATE`: A unix timestamp in milliseconds to use as the latest date when looking up transactions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
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
import aws_cdk.aws_dynamodb
import aws_cdk.aws_events
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_nodejs
import aws_cdk.aws_sns
import constructs


@jsii.data_type(
    jsii_type="fantasy-hockey-notifier-cdk.FantasyHockeyEnvVars",
    jsii_struct_bases=[],
    name_mapping={
        "discord_webhook": "discordWebhook",
        "espn_s2_cookie": "espnS2Cookie",
        "fh_league_id": "fhLeagueId",
        "fh_season": "fhSeason",
    },
)
class FantasyHockeyEnvVars:
    def __init__(
        self,
        *,
        discord_webhook: typing.Optional[builtins.str] = None,
        espn_s2_cookie: typing.Optional[builtins.str] = None,
        fh_league_id: typing.Optional[builtins.str] = None,
        fh_season: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Environment variables for the Lambda function.

        :param discord_webhook: Value for DISCORD_WEBHOOK.
        :param espn_s2_cookie: Value for ESPN_S2_COOKIE. This is a required parameter and must be set via SSM or clear text env vars
        :param fh_league_id: Value for FH_LEAGUE_ID. This is a required parameter and must be set via SSM or clear text env vars
        :param fh_season: Value for FH_SEASON. This is a required parameter and must be set via SSM or clear text env vars
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if discord_webhook is not None:
            self._values["discord_webhook"] = discord_webhook
        if espn_s2_cookie is not None:
            self._values["espn_s2_cookie"] = espn_s2_cookie
        if fh_league_id is not None:
            self._values["fh_league_id"] = fh_league_id
        if fh_season is not None:
            self._values["fh_season"] = fh_season

    @builtins.property
    def discord_webhook(self) -> typing.Optional[builtins.str]:
        '''Value for DISCORD_WEBHOOK.'''
        result = self._values.get("discord_webhook")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def espn_s2_cookie(self) -> typing.Optional[builtins.str]:
        '''Value for ESPN_S2_COOKIE.

        This is a required parameter and must be set via SSM or
        clear text env vars
        '''
        result = self._values.get("espn_s2_cookie")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fh_league_id(self) -> typing.Optional[builtins.str]:
        '''Value for FH_LEAGUE_ID.

        This is a required parameter and must be set via SSM or
        clear text env vars
        '''
        result = self._values.get("fh_league_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fh_season(self) -> typing.Optional[builtins.str]:
        '''Value for FH_SEASON.

        This is a required parameter and must be set via SSM or
        clear text env vars
        '''
        result = self._values.get("fh_season")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FantasyHockeyEnvVars(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FantasyHockeyNotifier(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fantasy-hockey-notifier-cdk.FantasyHockeyNotifier",
):
    '''A Lambda function to send notifications for transactions in an ESPN Fantasy Hockey league.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dynamo_table: typing.Optional[aws_cdk.aws_dynamodb.ITable] = None,
        dynamo_table_removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        env_var_values: typing.Optional[FantasyHockeyEnvVars] = None,
        kms_keys: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        lambda_architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        lambda_schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        sns_topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
        ssm_paths: typing.Optional[FantasyHockeyEnvVars] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''Constructor for FantasyHockeyNotifier.

        :param scope: Scope.
        :param id: ID.
        :param dynamo_table: An existing DynamoDB Table to use. Default: - a new Table will be created
        :param dynamo_table_removal_policy: The removal policy for the DynamoDB table. Default: RemovalPolicy.RETAIN
        :param env_var_values: Values for the env vars. If a value is specifed here and in ``ssmPaths``, the value in ``ssmPaths`` takes prescedence
        :param kms_keys: Existing KMS keys that are used to encrypt the SSM parameters. This must be specified to allow Lambda to read SecureString SSM parameteers
        :param lambda_architecture: The system architecture to use for the lambda function. Default: Architecture.ARM_64
        :param lambda_schedule: The schedule to use for the Lambda function. Default: Schedule.rate(Duration.minutes(1))
        :param memory_size: The amount of memory, in MB, to allocate to the Lambda function. Default: 128
        :param sns_topic: An existing SNS topic to send league event notifications to.
        :param ssm_paths: Paths for existing SSM parmeters with values for the env vars. If a value is specifed here and in ``envVarValues``, this value takes prescedence
        :param timeout: The function execution time after which Lambda terminates the function. Default: Duration.seconds(10)
        '''
        props = FantasyHockeyNotifierProps(
            dynamo_table=dynamo_table,
            dynamo_table_removal_policy=dynamo_table_removal_policy,
            env_var_values=env_var_values,
            kms_keys=kms_keys,
            lambda_architecture=lambda_architecture,
            lambda_schedule=lambda_schedule,
            memory_size=memory_size,
            sns_topic=sns_topic,
            ssm_paths=ssm_paths,
            timeout=timeout,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoTable")
    def dynamo_table(self) -> aws_cdk.aws_dynamodb.ITable:
        '''The DynamoDB Table used for storing state.'''
        return typing.cast(aws_cdk.aws_dynamodb.ITable, jsii.get(self, "dynamoTable"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dynamoTableRemovalPolicy")
    def dynamo_table_removal_policy(self) -> aws_cdk.RemovalPolicy:
        '''The removal policy for the DynamoDB table.'''
        return typing.cast(aws_cdk.RemovalPolicy, jsii.get(self, "dynamoTableRemovalPolicy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventRule")
    def event_rule(self) -> aws_cdk.aws_events.Rule:
        '''The event rule for the Lambda function.'''
        return typing.cast(aws_cdk.aws_events.Rule, jsii.get(self, "eventRule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaArchitecture")
    def lambda_architecture(self) -> aws_cdk.aws_lambda.Architecture:
        '''The system architecture for the Lambda function.'''
        return typing.cast(aws_cdk.aws_lambda.Architecture, jsii.get(self, "lambdaArchitecture"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda_nodejs.NodejsFunction:
        '''The Lambda function.'''
        return typing.cast(aws_cdk.aws_lambda_nodejs.NodejsFunction, jsii.get(self, "lambdaFunction"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="snsTopic")
    def sns_topic(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        '''The SNS topic that recieves notifications about league events.'''
        return typing.cast(typing.Optional[aws_cdk.aws_sns.ITopic], jsii.get(self, "snsTopic"))


@jsii.data_type(
    jsii_type="fantasy-hockey-notifier-cdk.FantasyHockeyNotifierProps",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_table": "dynamoTable",
        "dynamo_table_removal_policy": "dynamoTableRemovalPolicy",
        "env_var_values": "envVarValues",
        "kms_keys": "kmsKeys",
        "lambda_architecture": "lambdaArchitecture",
        "lambda_schedule": "lambdaSchedule",
        "memory_size": "memorySize",
        "sns_topic": "snsTopic",
        "ssm_paths": "ssmPaths",
        "timeout": "timeout",
    },
)
class FantasyHockeyNotifierProps:
    def __init__(
        self,
        *,
        dynamo_table: typing.Optional[aws_cdk.aws_dynamodb.ITable] = None,
        dynamo_table_removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        env_var_values: typing.Optional[FantasyHockeyEnvVars] = None,
        kms_keys: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        lambda_architecture: typing.Optional[aws_cdk.aws_lambda.Architecture] = None,
        lambda_schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        sns_topic: typing.Optional[aws_cdk.aws_sns.ITopic] = None,
        ssm_paths: typing.Optional[FantasyHockeyEnvVars] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''Properties for a FantasyHockeyNotifier.

        :param dynamo_table: An existing DynamoDB Table to use. Default: - a new Table will be created
        :param dynamo_table_removal_policy: The removal policy for the DynamoDB table. Default: RemovalPolicy.RETAIN
        :param env_var_values: Values for the env vars. If a value is specifed here and in ``ssmPaths``, the value in ``ssmPaths`` takes prescedence
        :param kms_keys: Existing KMS keys that are used to encrypt the SSM parameters. This must be specified to allow Lambda to read SecureString SSM parameteers
        :param lambda_architecture: The system architecture to use for the lambda function. Default: Architecture.ARM_64
        :param lambda_schedule: The schedule to use for the Lambda function. Default: Schedule.rate(Duration.minutes(1))
        :param memory_size: The amount of memory, in MB, to allocate to the Lambda function. Default: 128
        :param sns_topic: An existing SNS topic to send league event notifications to.
        :param ssm_paths: Paths for existing SSM parmeters with values for the env vars. If a value is specifed here and in ``envVarValues``, this value takes prescedence
        :param timeout: The function execution time after which Lambda terminates the function. Default: Duration.seconds(10)
        '''
        if isinstance(env_var_values, dict):
            env_var_values = FantasyHockeyEnvVars(**env_var_values)
        if isinstance(ssm_paths, dict):
            ssm_paths = FantasyHockeyEnvVars(**ssm_paths)
        self._values: typing.Dict[str, typing.Any] = {}
        if dynamo_table is not None:
            self._values["dynamo_table"] = dynamo_table
        if dynamo_table_removal_policy is not None:
            self._values["dynamo_table_removal_policy"] = dynamo_table_removal_policy
        if env_var_values is not None:
            self._values["env_var_values"] = env_var_values
        if kms_keys is not None:
            self._values["kms_keys"] = kms_keys
        if lambda_architecture is not None:
            self._values["lambda_architecture"] = lambda_architecture
        if lambda_schedule is not None:
            self._values["lambda_schedule"] = lambda_schedule
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if sns_topic is not None:
            self._values["sns_topic"] = sns_topic
        if ssm_paths is not None:
            self._values["ssm_paths"] = ssm_paths
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def dynamo_table(self) -> typing.Optional[aws_cdk.aws_dynamodb.ITable]:
        '''An existing DynamoDB Table to use.

        :default: - a new Table will be created
        '''
        result = self._values.get("dynamo_table")
        return typing.cast(typing.Optional[aws_cdk.aws_dynamodb.ITable], result)

    @builtins.property
    def dynamo_table_removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''The removal policy for the DynamoDB table.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("dynamo_table_removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def env_var_values(self) -> typing.Optional[FantasyHockeyEnvVars]:
        '''Values for the env vars.

        If a value is specifed here and in ``ssmPaths``, the value in ``ssmPaths`` takes prescedence
        '''
        result = self._values.get("env_var_values")
        return typing.cast(typing.Optional[FantasyHockeyEnvVars], result)

    @builtins.property
    def kms_keys(self) -> typing.Optional[typing.List[aws_cdk.aws_kms.IKey]]:
        '''Existing KMS keys that are used to encrypt the SSM parameters.

        This must be specified to allow Lambda to read SecureString SSM parameteers
        '''
        result = self._values.get("kms_keys")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_kms.IKey]], result)

    @builtins.property
    def lambda_architecture(self) -> typing.Optional[aws_cdk.aws_lambda.Architecture]:
        '''The system architecture to use for the lambda function.

        :default: Architecture.ARM_64
        '''
        result = self._values.get("lambda_architecture")
        return typing.cast(typing.Optional[aws_cdk.aws_lambda.Architecture], result)

    @builtins.property
    def lambda_schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''The schedule to use for the Lambda function.

        :default: Schedule.rate(Duration.minutes(1))
        '''
        result = self._values.get("lambda_schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''The amount of memory, in MB, to allocate to the Lambda function.

        :default: 128
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sns_topic(self) -> typing.Optional[aws_cdk.aws_sns.ITopic]:
        '''An existing SNS topic to send league event notifications to.'''
        result = self._values.get("sns_topic")
        return typing.cast(typing.Optional[aws_cdk.aws_sns.ITopic], result)

    @builtins.property
    def ssm_paths(self) -> typing.Optional[FantasyHockeyEnvVars]:
        '''Paths for existing SSM parmeters with values for the env vars.

        If a value is specifed here and in ``envVarValues``, this value takes prescedence
        '''
        result = self._values.get("ssm_paths")
        return typing.cast(typing.Optional[FantasyHockeyEnvVars], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''The function execution time after which Lambda terminates the function.

        :default: Duration.seconds(10)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FantasyHockeyNotifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FantasyHockeyEnvVars",
    "FantasyHockeyNotifier",
    "FantasyHockeyNotifierProps",
]

publication.publish()
