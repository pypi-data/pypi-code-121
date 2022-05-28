'''
# cdk-lex-zip-import

![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)

An AWS Cloud Development Kit (AWS CDK) construct library that allows you to upload and deploy a Zipped Lex Bot. Once imported, this Bot can be managed within the Amazon Lex Console.

## Usage

To add to your AWS CDK package.json file:

```
yarn add cdk-lex-zip-import
```

Within your AWS CDK:

### Import Lex Bot

```python
const bot = new lexupload.ImportBot(this, 'lexBot', {
  sourceDirectory: './resources/LexBot',
  lexRoleArn: lexRole.roleArn,
});
```

The `sourceDirecotry` must include a file named `LexBot.zip`. All files in that directory will be uploaded, but only a file named `LexBot.zip` will be imported to Lex as a Bot.

The `lexRoleArn` refers to the roleArn of an IAM Role. For example:

```python
const lexRole = new iam.Role(this, 'lexRole', {
  assumedBy: new iam.ServicePrincipal('lex.amazonaws.com'),
  inlinePolicies: {
    ['lexPolicy']: new iam.PolicyDocument({
      statements: [
        new iam.PolicyStatement({
          resources: ['*'],
          actions: ['polly:SynthesizeSpeech', 'comprehend:DetectSentiment'],
        }),
      ],
    }),
  },
});
```

### Adding a Resource Policy

```python
bot.addResourcePolicy(resourceArn, policy);
```

`addResourcePolicy` requires two properties: the `resourceArn` of the Lex Bot, and a policy to be applied. This policy will be applied to the alias associated with the Bot.

#### Resource ARN Example:

```python
const resourceArn = `arn:aws:lex:${this.region}:${this.account}:bot-alias/${bot.botId}/${bot.botAliasId}`;
```

#### Policy Example:

```python
const policy = {
  Version: '2012-10-17',
  Statement: [
    {
      Sid: 'AllowChimePstnAudioUseBot',
      Effect: 'Allow',
      Principal: { Service: 'voiceconnector.chime.amazonaws.com' },
      Action: 'lex:StartConversation',
      Resource: resourceArn,
      Condition: {
        StringEquals: { 'AWS:SourceAccount': `${this.account}` },
        ArnEquals: {
          'AWS:SourceArn': `arn:aws:voiceconnector:us-east-1:${this.account}:*`,
        },
      },
    },
  ],
};
```

## Not Supported Yet

This is a work in progress.

Features that are not supported yet:

* [ ] Non-Draft Versions
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
import aws_cdk.aws_s3
import constructs


class ImportBot(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lex-zip-import.ImportBot",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        lex_role_arn: builtins.str,
        source_directory: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param lex_role_arn: ARN for IAM Role associated with Lex Bot (required). Default: - None
        :param source_directory: Zip File location (required). Default: - None
        '''
        props = LexBotProps(
            lex_role_arn=lex_role_arn, source_directory=source_directory
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addResourcePolicy")
    def add_resource_policy(
        self,
        resource_arn: builtins.str,
        policy: typing.Mapping[typing.Any, typing.Any],
    ) -> "LexImportCustomResource":
        '''
        :param resource_arn: -
        :param policy: -
        '''
        return typing.cast("LexImportCustomResource", jsii.invoke(self, "addResourcePolicy", [resource_arn, policy]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botAliasId")
    def bot_alias_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "botAliasId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="botId")
    def bot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "botId"))


@jsii.data_type(
    jsii_type="cdk-lex-zip-import.LexBotProps",
    jsii_struct_bases=[],
    name_mapping={"lex_role_arn": "lexRoleArn", "source_directory": "sourceDirectory"},
)
class LexBotProps:
    def __init__(
        self,
        *,
        lex_role_arn: builtins.str,
        source_directory: builtins.str,
    ) -> None:
        '''Props for ``ImportBot``.

        :param lex_role_arn: ARN for IAM Role associated with Lex Bot (required). Default: - None
        :param source_directory: Zip File location (required). Default: - None
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "lex_role_arn": lex_role_arn,
            "source_directory": source_directory,
        }

    @builtins.property
    def lex_role_arn(self) -> builtins.str:
        '''ARN for IAM Role associated with Lex Bot (required).

        :default: - None
        '''
        result = self._values.get("lex_role_arn")
        assert result is not None, "Required property 'lex_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def source_directory(self) -> builtins.str:
        '''Zip File location (required).

        :default: - None
        '''
        result = self._values.get("source_directory")
        assert result is not None, "Required property 'source_directory' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexBotProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LexImportCustomResource(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-lex-zip-import.LexImportCustomResource",
):
    '''Adds "action" functionality to the Policy Statement.

    :private: true
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function: builtins.str,
        uid: builtins.str,
        lex_role_arn: typing.Optional[builtins.str] = None,
        lex_zip_bucket: typing.Optional[aws_cdk.aws_s3.Bucket] = None,
        policy: typing.Optional[typing.Mapping[typing.Any, typing.Any]] = None,
        resource_arn: typing.Optional[builtins.str] = None,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param function: 
        :param uid: 
        :param lex_role_arn: 
        :param lex_zip_bucket: 
        :param policy: 
        :param resource_arn: 
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        '''
        props = LexImportCustomResourceProps(
            function=function,
            uid=uid,
            lex_role_arn=lex_role_arn,
            lex_zip_bucket=lex_zip_bucket,
            policy=policy,
            resource_arn=resource_arn,
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
    @jsii.member(jsii_name="lexImport")
    def lex_import(self) -> aws_cdk.CustomResource:
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "lexImport"))


@jsii.data_type(
    jsii_type="cdk-lex-zip-import.LexImportCustomResourceProps",
    jsii_struct_bases=[aws_cdk.ResourceProps],
    name_mapping={
        "account": "account",
        "environment_from_arn": "environmentFromArn",
        "physical_name": "physicalName",
        "region": "region",
        "function": "function",
        "uid": "uid",
        "lex_role_arn": "lexRoleArn",
        "lex_zip_bucket": "lexZipBucket",
        "policy": "policy",
        "resource_arn": "resourceArn",
    },
)
class LexImportCustomResourceProps(aws_cdk.ResourceProps):
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        environment_from_arn: typing.Optional[builtins.str] = None,
        physical_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        function: builtins.str,
        uid: builtins.str,
        lex_role_arn: typing.Optional[builtins.str] = None,
        lex_zip_bucket: typing.Optional[aws_cdk.aws_s3.Bucket] = None,
        policy: typing.Optional[typing.Mapping[typing.Any, typing.Any]] = None,
        resource_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account: The AWS account ID this resource belongs to. Default: - the resource is in the same account as the stack it belongs to
        :param environment_from_arn: ARN to deduce region and account from. The ARN is parsed and the account and region are taken from the ARN. This should be used for imported resources. Cannot be supplied together with either ``account`` or ``region``. Default: - take environment from ``account``, ``region`` parameters, or use Stack environment.
        :param physical_name: The value passed in by users to the physical name prop of the resource. - ``undefined`` implies that a physical name will be allocated by CloudFormation during deployment. - a concrete value implies a specific physical name - ``PhysicalName.GENERATE_IF_NEEDED`` is a marker that indicates that a physical will only be generated by the CDK if it is needed for cross-environment references. Otherwise, it will be allocated by CloudFormation. Default: - The physical name will be allocated by CloudFormation at deployment time
        :param region: The AWS region this resource belongs to. Default: - the resource is in the same region as the stack it belongs to
        :param function: 
        :param uid: 
        :param lex_role_arn: 
        :param lex_zip_bucket: 
        :param policy: 
        :param resource_arn: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function": function,
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
        if lex_role_arn is not None:
            self._values["lex_role_arn"] = lex_role_arn
        if lex_zip_bucket is not None:
            self._values["lex_zip_bucket"] = lex_zip_bucket
        if policy is not None:
            self._values["policy"] = policy
        if resource_arn is not None:
            self._values["resource_arn"] = resource_arn

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
    def function(self) -> builtins.str:
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def uid(self) -> builtins.str:
        result = self._values.get("uid")
        assert result is not None, "Required property 'uid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def lex_role_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("lex_role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def lex_zip_bucket(self) -> typing.Optional[aws_cdk.aws_s3.Bucket]:
        result = self._values.get("lex_zip_bucket")
        return typing.cast(typing.Optional[aws_cdk.aws_s3.Bucket], result)

    @builtins.property
    def policy(self) -> typing.Optional[typing.Mapping[typing.Any, typing.Any]]:
        result = self._values.get("policy")
        return typing.cast(typing.Optional[typing.Mapping[typing.Any, typing.Any]], result)

    @builtins.property
    def resource_arn(self) -> typing.Optional[builtins.str]:
        result = self._values.get("resource_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LexImportCustomResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ImportBot",
    "LexBotProps",
    "LexImportCustomResource",
    "LexImportCustomResourceProps",
]

publication.publish()
