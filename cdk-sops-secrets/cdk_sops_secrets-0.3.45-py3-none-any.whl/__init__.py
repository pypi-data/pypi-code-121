'''
<img src="https://github.com/markussiebert/cdk-sops-secrets/raw/main/img/banner-dl-small.png?raw=True">
<p/>

[![cdk-construct-hub](https://img.shields.io/badge/CDK-ConstructHub-blue)](https://constructs.dev/packages/cdk-sops-secrets) 
![stability](https://img.shields.io/badge/Stability-experimental-red)<br>
[![npm](https://img.shields.io/npm/v/cdk-sops-secrets.svg)](https://www.npmjs.com/package/cdk-sops-secrets) 
[![npm downloads](https://img.shields.io/npm/dw/cdk-sops-secrets)]()<br>
[![pypi](https://img.shields.io/pypi/v/cdk-sops-secrets.svg)](https://pypi.org/project/cdk-sops-secrets) 
[![pypi downloads](https://img.shields.io/pypi/dw/cdk-sops-secrets)]()<br>
[![release](https://github.com/markussiebert/cdk-sops-secrets/actions/workflows/release.yml/badge.svg)](https://github.com/markussiebert/cdk-sops-secrets/actions/workflows/release.yml) 
[![codecov](https://codecov.io/gh/markussiebert/cdk-sops-secrets/branch/main/graph/badge.svg?token=OT7P7HQHXB)](https://codecov.io/gh/markussiebert/cdk-sops-secrets)  
[![security-vulnerabilities](https://img.shields.io/github/issues-search/markussiebert/cdk-sops-secrets?color=%23ff0000&label=security-vulnerabilities&query=is%3Aissue%20is%3Aopen%20label%3A%22security%20vulnerability%22)](https://github.com/markussiebert/cdk-sops-secrets/issues?q=is%3Aissue+is%3Aopen+label%3A%22security+vulnerability%22) 

## Introduction

This construct library provides a replacement for CDK SecretsManager secrets, with extended functionality for Mozilla/sops.

Using this library it is possible to populate Secrets with values from a Mozilla/sops file without additional scripts and steps in the CI stage. Thereby transformations like JSON conversion of YAML files and transformation into a flat, JSONPath like structure will be performed, but can be disabled.

Secrets filled in this way can be used immediately within the CloudFormation stack and dynamic references. This construct should handle all dependencies, if you use the `secretValueFromJson()` or `secretValue()` call to access secret values.

This way, secrets can be securely stored in git repositories and easily synchronized into AWS SecretsManager secrets.

## Stability

This is an early version of the package. At the moment, I would classify this library as experimental — API changes or changes to the default behavior may occur and may not follow semver. Please pin the exact version of this library in your `package.json`.

## Prerequisites

* [AWS](https://aws.amazon.com/): I think you already knew it, but this construct will only work with an AWS account.

* [KMS Key](https://aws.amazon.com/kms/?nc1=h_ls): It makes most sense to encrypt your secrets with AWS KMS if you want to sync and use the secret content afterwards in your AWS account.
* [mozilla/sops](https://github.com/mozilla/sops): This construct assumes that you store your secrets encrypted via sops in your git repository.
* [CDK](https://aws.amazon.com/cdk/?nc1=h_ls): As this is a CDK construct, it's only useful if you use the CloudDevelopmentToolkit.

## Getting started

1. Create a Mozilla/sops secrets file (encrypted with an already existing KMS key) and place it somewhere in your git repository
2. Create a secret with the SopsSecret construct inside your app

   ```python
   const secret = new SopsSecret(stack, 'SopsComplexSecretJSON', {
     sopsFilePath: 'secets/sopsfile-encrypted.json',
   });
   ```
3. Optional: Access the secret via dynamic references

   ```python
   secret.secretValueFromJson('json.path.dotted.notation.accessor[0]').toString(),
   ```

## Advanced configuration examples

Even if using the main functionality should be done in 3 lines of code, there are more options to configure the constructs of this library. If you want to get an Overview of all available configuration options take a look at the [documentation at the CDK ConstructHub](https://constructs.dev/packages/cdk-sops-secrets).

The most useful settings will be explained in the further chapters:

### Default conversions and how to disable them?

As default behavior, the SopsSecret (via the SopsSync) will convert all content to JSON and flatten its structure. This is useful, because the AWS SecretsManager has some limitations if it comes to YAML and/or complex objects and decimal values. Even if you can store YAML, complex objects and even binaries in AWS SecretsManager secrets, you can't access their values via the SecretsManager API — you can only return them as is. So accessing (nested) values or values from YAML files won't be possible via [dynamic references](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html) in CloudFormation (and CDK). That's why I decided that conversion to JSON, flatten the structure and stringify all values should be the default behavior. But you can turn off all of these conversion steps:

```python
const secret = new SopsSecret(this, 'SopsComplexSecretJSON', {
  convertToJSON: false, // disable converting the encrypted content to JSON
  stringify: false, // disable stringifying all values
  flatten: false, // disable flattening of the object structure
  sopsFilePath: 'secrets/sopsfile-encrypted.json',
});
```

### Resource provider is missing permissions

Sometimes it can be necessary to access the IAM role of the SopsSync provider. If this is the case, you should create the provider before creating the SopsSecret, and pass the provider to it like this:

```python
// Create the provider
const provider = new SopsSyncProvider(this, 'CustomSopsSyncProvider');
// Grant whatever you need to the provider
const myExtraKmsKey = Key.fromKeyArn(this, 'MyExtraKmsKey', 'YourKeyArn');
myExtraKmsKey.grantDecrypt(provider);
// create the secret and pass the the provider to it
const secret = new SopsSecret(this, 'SopsComplexSecretJSON', {
  sopsProvider: provider,
  secretName: 'myCoolSecret',
  sopsFilePath: 'secrets/sopsfile-encrypted.json',
});
```

### UploadType: INLINE / ASSET

I decided, that the default behavior should be "INLINE" because of the following consideration:

* Fewer permissions: If we use inline content instead of a S3 asset, the SopsSyncProvider does not need permissions to access the asset bucket and its KMS key.
* Faster: If we don't have to upload and download things from and to S3, it should be a little faster.
* Interchangeable: As we use the same information to generate the version of the secret, no new version of the secret should be created, if you change from INLINE to ASSET or vice versa, even if the CloudFormation resource updates.
* I personally think sops files are not that big, that we should run into limits, but if so — we can change to asset `uploadType`.

You can change the uplaodType via the properties:

```python
const secret = new SopsSecret(this, 'SopsWithAssetUpload', {
  sopsFilePath: 'secrets/sopsfile-encrypted.json',
  uploadType: UploadType.ASSET, // instead of the default UploadType.INLINE
});
```

## FAQ

### It does not work, what can I do?

Even if this construct has some unit and integration tests performed, there can be bugs and issues. As everything is performed by a cloudformation custom resource provider, a good starting point is the log of the corresponding lambda function. It should be located in your AWS Account under Cloudwatch -> Log groups:

`/aws/lambda/<YOUR-STACK-NAME>-SingletonLambdaSopsSyncProvider<SOMETHINGsomething1234>`

### Error getting data key: 0 successful groups required, got 0

This error message (and failed sync) is related to the  mozilla/sops issues [#948](https://github.com/mozilla/sops/issues/948) and [#634](https://github.com/mozilla/sops/issues/634). You must not create your secret with the `--aws-profile` flag. This profile will be written to your sops filed and is required in every runtime environment. You have to define the profile to use via the environment variable `AWS_PROFILE` instead, to avoid this.

## Motivation

I have created this project to solve a recurring problem of syncing Mozilla/sops secrets into AWS SecretsManager in a convenient, secure way.

Other than that, or perhaps more importantly, my goal was to learn new things:

* Write a Golang lambda
* Writing unit tests incl. mocks in Golang
* Reproducible builds of Golang binaries (byte-by-byte identical)
* Build reproducible zips (byte-by-byte identical)
* Release a NPM package
* Setting up projects with projen
* CI/CD with GitHub actions
* CDK unit and integration tests

## Other Tools like this

The problem this Construct addresses is so good, already two other implementations exist:

* [isotoma/sops-secretsmanager-cdk](https://github.com/isotoma/sops-secretsmanager-cdk): Does nearly the same. Uses CustomResource, wraps the sops CLI, does not support flatten. Found it after I published my solution to NPM :-/
* [taimos/secretsmanager-versioning](https://github.com/taimos/secretsmanager-versioning): Different approach on the same problem. This is a CLI tool with very nice integration into CDK and also handles git versioning information.
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
import aws_cdk.aws_kms
import aws_cdk.aws_lambda
import aws_cdk.aws_secretsmanager
import constructs


@jsii.implements(aws_cdk.aws_secretsmanager.ISecret)
class SopsSecret(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-sops-secrets.SopsSecret",
):
    '''(experimental) A drop in replacement for the normal Secret, that is populated with the encrypted content of the given sops file.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        generate_secret_string: typing.Optional[aws_cdk.aws_secretsmanager.SecretStringGenerator] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        replica_regions: typing.Optional[typing.Sequence[aws_cdk.aws_secretsmanager.ReplicaRegion]] = None,
        secret_name: typing.Optional[builtins.str] = None,
        sops_file_path: builtins.str,
        convert_to_json: typing.Optional[builtins.bool] = None,
        flatten: typing.Optional[builtins.bool] = None,
        sops_age_key: typing.Optional[aws_cdk.SecretValue] = None,
        sops_file_format: typing.Optional[builtins.str] = None,
        sops_kms_key: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        sops_provider: typing.Optional["SopsSyncProvider"] = None,
        stringify_values: typing.Optional[builtins.bool] = None,
        upload_type: typing.Optional["UploadType"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: An optional, human-friendly description of the secret. Default: - No description.
        :param encryption_key: The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.
        :param generate_secret_string: Configuration for how to generate a secret value. Default: - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each category), per the default values of ``SecretStringGenerator``.
        :param removal_policy: Policy to apply when the secret is removed from this stack. Default: - Not set.
        :param replica_regions: A list of regions where to replicate this secret. Default: - Secret is not replicated
        :param secret_name: A name for the secret. Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to 30 days blackout period. During that period, it is not possible to create another secret that shares the same name. Default: - A name is generated by CloudFormation.
        :param sops_file_path: (experimental) The filepath to the sops file.
        :param convert_to_json: (experimental) Should the encrypted sops value should be converted to JSON? Only JSON can be handled by cloud formations dynamic references. Default: true
        :param flatten: (experimental) Should the structure be flattened? The result will be a flat structure and all object keys will be replaced with the full jsonpath as key. This is usefull for dynamic references, as those don't support nested objects. Default: true
        :param sops_age_key: (experimental) The age key that should be used for encryption.
        :param sops_file_format: (experimental) The format of the sops file. Default: - The fileformat will be derived from the file ending
        :param sops_kms_key: (experimental) The kmsKey used to encrypt the sops file. Encrypt permissions will be granted to the custom resource provider. Default: - The key will be derived from the sops file
        :param sops_provider: (experimental) The custom resource provider to use. If you don't specify any, a new provider will be created - or if already exists within this stack - reused. Default: - A new singleton provider will be created
        :param stringify_values: (experimental) Shall all values be flattened? This is usefull for dynamic references, as there are lookup errors for certain float types
        :param upload_type: (experimental) How should the secret be passed to the CustomResource? Default: INLINE

        :stability: experimental
        '''
        props = SopsSecretProps(
            description=description,
            encryption_key=encryption_key,
            generate_secret_string=generate_secret_string,
            removal_policy=removal_policy,
            replica_regions=replica_regions,
            secret_name=secret_name,
            sops_file_path=sops_file_path,
            convert_to_json=convert_to_json,
            flatten=flatten,
            sops_age_key=sops_age_key,
            sops_file_format=sops_file_format,
            sops_kms_key=sops_kms_key,
            sops_provider=sops_provider,
            stringify_values=stringify_values,
            upload_type=upload_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addRotationSchedule")
    def add_rotation_schedule(
        self,
        id: builtins.str,
        *,
        automatically_after: typing.Optional[aws_cdk.Duration] = None,
        hosted_rotation: typing.Optional[aws_cdk.aws_secretsmanager.HostedRotation] = None,
        rotation_lambda: typing.Optional[aws_cdk.aws_lambda.IFunction] = None,
    ) -> aws_cdk.aws_secretsmanager.RotationSchedule:
        '''(experimental) Adds a rotation schedule to the secret.

        :param id: -
        :param automatically_after: Specifies the number of days after the previous rotation before Secrets Manager triggers the next automatic rotation. Default: Duration.days(30)
        :param hosted_rotation: Hosted rotation. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified
        :param rotation_lambda: A Lambda function that can rotate the secret. Default: - either ``rotationLambda`` or ``hostedRotation`` must be specified

        :stability: experimental
        '''
        options = aws_cdk.aws_secretsmanager.RotationScheduleOptions(
            automatically_after=automatically_after,
            hosted_rotation=hosted_rotation,
            rotation_lambda=rotation_lambda,
        )

        return typing.cast(aws_cdk.aws_secretsmanager.RotationSchedule, jsii.invoke(self, "addRotationSchedule", [id, options]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: aws_cdk.aws_iam.PolicyStatement,
    ) -> aws_cdk.aws_iam.AddToResourcePolicyResult:
        '''(experimental) Adds a statement to the IAM resource policy associated with this secret.

        If this secret was created in this stack, a resource policy will be
        automatically created upon the first call to ``addToResourcePolicy``. If
        the secret is imported, then this is a no-op.

        :param statement: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="applyRemovalPolicy")
    def apply_removal_policy(self, policy: aws_cdk.RemovalPolicy) -> None:
        '''(experimental) Apply the given removal policy to this resource.

        The Removal Policy controls what happens to this resource when it stops
        being managed by CloudFormation, either because you've removed it from the
        CDK application or because you've made a change that requires the resource
        to be replaced.

        The resource can be deleted (``RemovalPolicy.DESTROY``), or left in your AWS
        account for data recovery and cleanup later (``RemovalPolicy.RETAIN``).

        :param policy: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "applyRemovalPolicy", [policy]))

    @jsii.member(jsii_name="attach")
    def attach(
        self,
        target: aws_cdk.aws_secretsmanager.ISecretAttachmentTarget,
    ) -> aws_cdk.aws_secretsmanager.ISecret:
        '''(experimental) Attach a target to this secret.

        :param target: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.invoke(self, "attach", [target]))

    @jsii.member(jsii_name="currentVersionId")
    def current_version_id(self) -> builtins.str:
        '''(experimental) Returns the current versionId that was created via the SopsSync.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "currentVersionId", []))

    @jsii.member(jsii_name="denyAccountRootDelete")
    def deny_account_root_delete(self) -> None:
        '''(experimental) Denies the ``DeleteSecret`` action to all principals within the current account.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "denyAccountRootDelete", []))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: aws_cdk.aws_iam.IGrantable,
        version_stages: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grants reading the secret value to some role.

        :param grantee: -
        :param version_stages: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantRead", [grantee, version_stages]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        _grantee: aws_cdk.aws_iam.IGrantable,
    ) -> aws_cdk.aws_iam.Grant:
        '''(experimental) Grants writing and updating the secret value to some role.

        :param _grantee: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.Grant, jsii.invoke(self, "grantWrite", [_grantee]))

    @jsii.member(jsii_name="secretValueFromJson")
    def secret_value_from_json(self, json_field: builtins.str) -> aws_cdk.SecretValue:
        '''(experimental) Interpret the secret as a JSON object and return a field's value from it as a ``SecretValue``.

        :param json_field: -

        :stability: experimental
        '''
        return typing.cast(aws_cdk.SecretValue, jsii.invoke(self, "secretValueFromJson", [json_field]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> aws_cdk.ResourceEnvironment:
        '''(experimental) The environment this resource belongs to.

        For resources that are created and managed by the CDK
        (generally, those created by creating new class instances like Role, Bucket, etc.),
        this is always the same as the environment of the stack they belong to;
        however, for imported resources
        (those obtained from static methods like fromRoleArn, fromBucketName, etc.),
        that might be different than the stack they were imported into.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.ResourceEnvironment, jsii.get(self, "env"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretArn")
    def secret_arn(self) -> builtins.str:
        '''(experimental) The ARN of the secret in AWS Secrets Manager.

        Will return the full ARN if available, otherwise a partial arn.
        For secrets imported by the deprecated ``fromSecretName``, it will return the ``secretName``.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> builtins.str:
        '''(experimental) The name of the secret.

        For "owned" secrets, this will be the full resource name (secret name + suffix), unless the
        '@aws-cdk/aws-secretsmanager:parseOwnedSecretName' feature flag is set.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "secretName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretValue")
    def secret_value(self) -> aws_cdk.SecretValue:
        '''(experimental) Retrieve the value of the stored secret as a ``SecretValue``.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.SecretValue, jsii.get(self, "secretValue"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stack")
    def stack(self) -> aws_cdk.Stack:
        '''(experimental) The stack in which this resource is defined.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.Stack, jsii.get(self, "stack"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sync")
    def sync(self) -> "SopsSync":
        '''
        :stability: experimental
        '''
        return typing.cast("SopsSync", jsii.get(self, "sync"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''(experimental) The customer-managed encryption key that is used to encrypt this secret, if any.

        When not specified, the default
        KMS key for the account and region is being used.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretFullArn")
    def secret_full_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The full ARN of the secret in AWS Secrets Manager, which is the ARN including the Secrets Manager-supplied 6-character suffix.

        This is equal to ``secretArn`` in most cases, but is undefined when a full ARN is not available (e.g., secrets imported by name).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretFullArn"))


class SopsSync(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-sops-secrets.SopsSync",
):
    '''(experimental) The custom resource, that is syncing the content from a sops file to a secret.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        secret: aws_cdk.aws_secretsmanager.ISecret,
        sops_file_path: builtins.str,
        convert_to_json: typing.Optional[builtins.bool] = None,
        flatten: typing.Optional[builtins.bool] = None,
        sops_age_key: typing.Optional[aws_cdk.SecretValue] = None,
        sops_file_format: typing.Optional[builtins.str] = None,
        sops_kms_key: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        sops_provider: typing.Optional["SopsSyncProvider"] = None,
        stringify_values: typing.Optional[builtins.bool] = None,
        upload_type: typing.Optional["UploadType"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param secret: (experimental) The secret that will be populated with the encrypted sops file content.
        :param sops_file_path: (experimental) The filepath to the sops file.
        :param convert_to_json: (experimental) Should the encrypted sops value should be converted to JSON? Only JSON can be handled by cloud formations dynamic references. Default: true
        :param flatten: (experimental) Should the structure be flattened? The result will be a flat structure and all object keys will be replaced with the full jsonpath as key. This is usefull for dynamic references, as those don't support nested objects. Default: true
        :param sops_age_key: (experimental) The age key that should be used for encryption.
        :param sops_file_format: (experimental) The format of the sops file. Default: - The fileformat will be derived from the file ending
        :param sops_kms_key: (experimental) The kmsKey used to encrypt the sops file. Encrypt permissions will be granted to the custom resource provider. Default: - The key will be derived from the sops file
        :param sops_provider: (experimental) The custom resource provider to use. If you don't specify any, a new provider will be created - or if already exists within this stack - reused. Default: - A new singleton provider will be created
        :param stringify_values: (experimental) Shall all values be flattened? This is usefull for dynamic references, as there are lookup errors for certain float types
        :param upload_type: (experimental) How should the secret be passed to the CustomResource? Default: INLINE

        :stability: experimental
        '''
        props = SopsSyncProps(
            secret=secret,
            sops_file_path=sops_file_path,
            convert_to_json=convert_to_json,
            flatten=flatten,
            sops_age_key=sops_age_key,
            sops_file_format=sops_file_format,
            sops_kms_key=sops_kms_key,
            sops_provider=sops_provider,
            stringify_values=stringify_values,
            upload_type=upload_type,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="converToJSON")
    def conver_to_json(self) -> builtins.bool:
        '''(experimental) Was the format converted to json?

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "converToJSON"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="flatten")
    def flatten(self) -> builtins.bool:
        '''(experimental) Was the structure flattened?

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "flatten"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sopsFileFormat")
    def sops_file_format(self) -> builtins.str:
        '''(experimental) The format of the input file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "sopsFileFormat"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stringifiedValues")
    def stringified_values(self) -> builtins.bool:
        '''(experimental) Were the values stringified?

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "stringifiedValues"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="versionId")
    def version_id(self) -> builtins.str:
        '''(experimental) The current versionId of the secret populated via this resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "versionId"))


@jsii.data_type(
    jsii_type="cdk-sops-secrets.SopsSyncOptions",
    jsii_struct_bases=[],
    name_mapping={
        "sops_file_path": "sopsFilePath",
        "convert_to_json": "convertToJSON",
        "flatten": "flatten",
        "sops_age_key": "sopsAgeKey",
        "sops_file_format": "sopsFileFormat",
        "sops_kms_key": "sopsKmsKey",
        "sops_provider": "sopsProvider",
        "stringify_values": "stringifyValues",
        "upload_type": "uploadType",
    },
)
class SopsSyncOptions:
    def __init__(
        self,
        *,
        sops_file_path: builtins.str,
        convert_to_json: typing.Optional[builtins.bool] = None,
        flatten: typing.Optional[builtins.bool] = None,
        sops_age_key: typing.Optional[aws_cdk.SecretValue] = None,
        sops_file_format: typing.Optional[builtins.str] = None,
        sops_kms_key: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        sops_provider: typing.Optional["SopsSyncProvider"] = None,
        stringify_values: typing.Optional[builtins.bool] = None,
        upload_type: typing.Optional["UploadType"] = None,
    ) -> None:
        '''(experimental) Configuration options for the SopsSync.

        :param sops_file_path: (experimental) The filepath to the sops file.
        :param convert_to_json: (experimental) Should the encrypted sops value should be converted to JSON? Only JSON can be handled by cloud formations dynamic references. Default: true
        :param flatten: (experimental) Should the structure be flattened? The result will be a flat structure and all object keys will be replaced with the full jsonpath as key. This is usefull for dynamic references, as those don't support nested objects. Default: true
        :param sops_age_key: (experimental) The age key that should be used for encryption.
        :param sops_file_format: (experimental) The format of the sops file. Default: - The fileformat will be derived from the file ending
        :param sops_kms_key: (experimental) The kmsKey used to encrypt the sops file. Encrypt permissions will be granted to the custom resource provider. Default: - The key will be derived from the sops file
        :param sops_provider: (experimental) The custom resource provider to use. If you don't specify any, a new provider will be created - or if already exists within this stack - reused. Default: - A new singleton provider will be created
        :param stringify_values: (experimental) Shall all values be flattened? This is usefull for dynamic references, as there are lookup errors for certain float types
        :param upload_type: (experimental) How should the secret be passed to the CustomResource? Default: INLINE

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "sops_file_path": sops_file_path,
        }
        if convert_to_json is not None:
            self._values["convert_to_json"] = convert_to_json
        if flatten is not None:
            self._values["flatten"] = flatten
        if sops_age_key is not None:
            self._values["sops_age_key"] = sops_age_key
        if sops_file_format is not None:
            self._values["sops_file_format"] = sops_file_format
        if sops_kms_key is not None:
            self._values["sops_kms_key"] = sops_kms_key
        if sops_provider is not None:
            self._values["sops_provider"] = sops_provider
        if stringify_values is not None:
            self._values["stringify_values"] = stringify_values
        if upload_type is not None:
            self._values["upload_type"] = upload_type

    @builtins.property
    def sops_file_path(self) -> builtins.str:
        '''(experimental) The filepath to the sops file.

        :stability: experimental
        '''
        result = self._values.get("sops_file_path")
        assert result is not None, "Required property 'sops_file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def convert_to_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the encrypted sops value should be converted to JSON?

        Only JSON can be handled by cloud formations dynamic references.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("convert_to_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def flatten(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the structure be flattened?

        The result will be a flat structure and all
        object keys will be replaced with the full jsonpath as key.
        This is usefull for dynamic references, as those don't support nested objects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("flatten")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sops_age_key(self) -> typing.Optional[aws_cdk.SecretValue]:
        '''(experimental) The age key that should be used for encryption.

        :stability: experimental
        '''
        result = self._values.get("sops_age_key")
        return typing.cast(typing.Optional[aws_cdk.SecretValue], result)

    @builtins.property
    def sops_file_format(self) -> typing.Optional[builtins.str]:
        '''(experimental) The format of the sops file.

        :default: - The fileformat will be derived from the file ending

        :stability: experimental
        '''
        result = self._values.get("sops_file_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sops_kms_key(self) -> typing.Optional[typing.List[aws_cdk.aws_kms.IKey]]:
        '''(experimental) The kmsKey used to encrypt the sops file.

        Encrypt permissions
        will be granted to the custom resource provider.

        :default: - The key will be derived from the sops file

        :stability: experimental
        '''
        result = self._values.get("sops_kms_key")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_kms.IKey]], result)

    @builtins.property
    def sops_provider(self) -> typing.Optional["SopsSyncProvider"]:
        '''(experimental) The custom resource provider to use.

        If you don't specify any, a new
        provider will be created - or if already exists within this stack - reused.

        :default: - A new singleton provider will be created

        :stability: experimental
        '''
        result = self._values.get("sops_provider")
        return typing.cast(typing.Optional["SopsSyncProvider"], result)

    @builtins.property
    def stringify_values(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Shall all values be flattened?

        This is usefull for dynamic references, as there
        are lookup errors for certain float types

        :stability: experimental
        '''
        result = self._values.get("stringify_values")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def upload_type(self) -> typing.Optional["UploadType"]:
        '''(experimental) How should the secret be passed to the CustomResource?

        :default: INLINE

        :stability: experimental
        '''
        result = self._values.get("upload_type")
        return typing.cast(typing.Optional["UploadType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SopsSyncOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-sops-secrets.SopsSyncProps",
    jsii_struct_bases=[SopsSyncOptions],
    name_mapping={
        "sops_file_path": "sopsFilePath",
        "convert_to_json": "convertToJSON",
        "flatten": "flatten",
        "sops_age_key": "sopsAgeKey",
        "sops_file_format": "sopsFileFormat",
        "sops_kms_key": "sopsKmsKey",
        "sops_provider": "sopsProvider",
        "stringify_values": "stringifyValues",
        "upload_type": "uploadType",
        "secret": "secret",
    },
)
class SopsSyncProps(SopsSyncOptions):
    def __init__(
        self,
        *,
        sops_file_path: builtins.str,
        convert_to_json: typing.Optional[builtins.bool] = None,
        flatten: typing.Optional[builtins.bool] = None,
        sops_age_key: typing.Optional[aws_cdk.SecretValue] = None,
        sops_file_format: typing.Optional[builtins.str] = None,
        sops_kms_key: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        sops_provider: typing.Optional["SopsSyncProvider"] = None,
        stringify_values: typing.Optional[builtins.bool] = None,
        upload_type: typing.Optional["UploadType"] = None,
        secret: aws_cdk.aws_secretsmanager.ISecret,
    ) -> None:
        '''(experimental) The configuration options extended by the target Secret.

        :param sops_file_path: (experimental) The filepath to the sops file.
        :param convert_to_json: (experimental) Should the encrypted sops value should be converted to JSON? Only JSON can be handled by cloud formations dynamic references. Default: true
        :param flatten: (experimental) Should the structure be flattened? The result will be a flat structure and all object keys will be replaced with the full jsonpath as key. This is usefull for dynamic references, as those don't support nested objects. Default: true
        :param sops_age_key: (experimental) The age key that should be used for encryption.
        :param sops_file_format: (experimental) The format of the sops file. Default: - The fileformat will be derived from the file ending
        :param sops_kms_key: (experimental) The kmsKey used to encrypt the sops file. Encrypt permissions will be granted to the custom resource provider. Default: - The key will be derived from the sops file
        :param sops_provider: (experimental) The custom resource provider to use. If you don't specify any, a new provider will be created - or if already exists within this stack - reused. Default: - A new singleton provider will be created
        :param stringify_values: (experimental) Shall all values be flattened? This is usefull for dynamic references, as there are lookup errors for certain float types
        :param upload_type: (experimental) How should the secret be passed to the CustomResource? Default: INLINE
        :param secret: (experimental) The secret that will be populated with the encrypted sops file content.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "sops_file_path": sops_file_path,
            "secret": secret,
        }
        if convert_to_json is not None:
            self._values["convert_to_json"] = convert_to_json
        if flatten is not None:
            self._values["flatten"] = flatten
        if sops_age_key is not None:
            self._values["sops_age_key"] = sops_age_key
        if sops_file_format is not None:
            self._values["sops_file_format"] = sops_file_format
        if sops_kms_key is not None:
            self._values["sops_kms_key"] = sops_kms_key
        if sops_provider is not None:
            self._values["sops_provider"] = sops_provider
        if stringify_values is not None:
            self._values["stringify_values"] = stringify_values
        if upload_type is not None:
            self._values["upload_type"] = upload_type

    @builtins.property
    def sops_file_path(self) -> builtins.str:
        '''(experimental) The filepath to the sops file.

        :stability: experimental
        '''
        result = self._values.get("sops_file_path")
        assert result is not None, "Required property 'sops_file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def convert_to_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the encrypted sops value should be converted to JSON?

        Only JSON can be handled by cloud formations dynamic references.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("convert_to_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def flatten(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the structure be flattened?

        The result will be a flat structure and all
        object keys will be replaced with the full jsonpath as key.
        This is usefull for dynamic references, as those don't support nested objects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("flatten")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sops_age_key(self) -> typing.Optional[aws_cdk.SecretValue]:
        '''(experimental) The age key that should be used for encryption.

        :stability: experimental
        '''
        result = self._values.get("sops_age_key")
        return typing.cast(typing.Optional[aws_cdk.SecretValue], result)

    @builtins.property
    def sops_file_format(self) -> typing.Optional[builtins.str]:
        '''(experimental) The format of the sops file.

        :default: - The fileformat will be derived from the file ending

        :stability: experimental
        '''
        result = self._values.get("sops_file_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sops_kms_key(self) -> typing.Optional[typing.List[aws_cdk.aws_kms.IKey]]:
        '''(experimental) The kmsKey used to encrypt the sops file.

        Encrypt permissions
        will be granted to the custom resource provider.

        :default: - The key will be derived from the sops file

        :stability: experimental
        '''
        result = self._values.get("sops_kms_key")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_kms.IKey]], result)

    @builtins.property
    def sops_provider(self) -> typing.Optional["SopsSyncProvider"]:
        '''(experimental) The custom resource provider to use.

        If you don't specify any, a new
        provider will be created - or if already exists within this stack - reused.

        :default: - A new singleton provider will be created

        :stability: experimental
        '''
        result = self._values.get("sops_provider")
        return typing.cast(typing.Optional["SopsSyncProvider"], result)

    @builtins.property
    def stringify_values(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Shall all values be flattened?

        This is usefull for dynamic references, as there
        are lookup errors for certain float types

        :stability: experimental
        '''
        result = self._values.get("stringify_values")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def upload_type(self) -> typing.Optional["UploadType"]:
        '''(experimental) How should the secret be passed to the CustomResource?

        :default: INLINE

        :stability: experimental
        '''
        result = self._values.get("upload_type")
        return typing.cast(typing.Optional["UploadType"], result)

    @builtins.property
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''(experimental) The secret that will be populated with the encrypted sops file content.

        :stability: experimental
        '''
        result = self._values.get("secret")
        assert result is not None, "Required property 'secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SopsSyncProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_iam.IGrantable)
class SopsSyncProvider(
    aws_cdk.aws_lambda.SingletonFunction,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-sops-secrets.SopsSyncProvider",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="addAgeKey")
    def add_age_key(self, key: aws_cdk.SecretValue) -> None:
        '''
        :param key: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addAgeKey", [key]))


@jsii.enum(jsii_type="cdk-sops-secrets.UploadType")
class UploadType(enum.Enum):
    '''
    :stability: experimental
    '''

    INLINE = "INLINE"
    '''(experimental) Pass the secret data inline (base64 encoded and compressed).

    :stability: experimental
    '''
    ASSET = "ASSET"
    '''(experimental) Uplaod the secert data as asset.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="cdk-sops-secrets.SopsSecretProps",
    jsii_struct_bases=[aws_cdk.aws_secretsmanager.SecretProps, SopsSyncOptions],
    name_mapping={
        "description": "description",
        "encryption_key": "encryptionKey",
        "generate_secret_string": "generateSecretString",
        "removal_policy": "removalPolicy",
        "replica_regions": "replicaRegions",
        "secret_name": "secretName",
        "sops_file_path": "sopsFilePath",
        "convert_to_json": "convertToJSON",
        "flatten": "flatten",
        "sops_age_key": "sopsAgeKey",
        "sops_file_format": "sopsFileFormat",
        "sops_kms_key": "sopsKmsKey",
        "sops_provider": "sopsProvider",
        "stringify_values": "stringifyValues",
        "upload_type": "uploadType",
    },
)
class SopsSecretProps(aws_cdk.aws_secretsmanager.SecretProps, SopsSyncOptions):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[aws_cdk.aws_kms.IKey] = None,
        generate_secret_string: typing.Optional[aws_cdk.aws_secretsmanager.SecretStringGenerator] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        replica_regions: typing.Optional[typing.Sequence[aws_cdk.aws_secretsmanager.ReplicaRegion]] = None,
        secret_name: typing.Optional[builtins.str] = None,
        sops_file_path: builtins.str,
        convert_to_json: typing.Optional[builtins.bool] = None,
        flatten: typing.Optional[builtins.bool] = None,
        sops_age_key: typing.Optional[aws_cdk.SecretValue] = None,
        sops_file_format: typing.Optional[builtins.str] = None,
        sops_kms_key: typing.Optional[typing.Sequence[aws_cdk.aws_kms.IKey]] = None,
        sops_provider: typing.Optional[SopsSyncProvider] = None,
        stringify_values: typing.Optional[builtins.bool] = None,
        upload_type: typing.Optional[UploadType] = None,
    ) -> None:
        '''(experimental) The configuration options of the SopsSecret.

        :param description: An optional, human-friendly description of the secret. Default: - No description.
        :param encryption_key: The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.
        :param generate_secret_string: Configuration for how to generate a secret value. Default: - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each category), per the default values of ``SecretStringGenerator``.
        :param removal_policy: Policy to apply when the secret is removed from this stack. Default: - Not set.
        :param replica_regions: A list of regions where to replicate this secret. Default: - Secret is not replicated
        :param secret_name: A name for the secret. Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to 30 days blackout period. During that period, it is not possible to create another secret that shares the same name. Default: - A name is generated by CloudFormation.
        :param sops_file_path: (experimental) The filepath to the sops file.
        :param convert_to_json: (experimental) Should the encrypted sops value should be converted to JSON? Only JSON can be handled by cloud formations dynamic references. Default: true
        :param flatten: (experimental) Should the structure be flattened? The result will be a flat structure and all object keys will be replaced with the full jsonpath as key. This is usefull for dynamic references, as those don't support nested objects. Default: true
        :param sops_age_key: (experimental) The age key that should be used for encryption.
        :param sops_file_format: (experimental) The format of the sops file. Default: - The fileformat will be derived from the file ending
        :param sops_kms_key: (experimental) The kmsKey used to encrypt the sops file. Encrypt permissions will be granted to the custom resource provider. Default: - The key will be derived from the sops file
        :param sops_provider: (experimental) The custom resource provider to use. If you don't specify any, a new provider will be created - or if already exists within this stack - reused. Default: - A new singleton provider will be created
        :param stringify_values: (experimental) Shall all values be flattened? This is usefull for dynamic references, as there are lookup errors for certain float types
        :param upload_type: (experimental) How should the secret be passed to the CustomResource? Default: INLINE

        :stability: experimental
        '''
        if isinstance(generate_secret_string, dict):
            generate_secret_string = aws_cdk.aws_secretsmanager.SecretStringGenerator(**generate_secret_string)
        self._values: typing.Dict[str, typing.Any] = {
            "sops_file_path": sops_file_path,
        }
        if description is not None:
            self._values["description"] = description
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if generate_secret_string is not None:
            self._values["generate_secret_string"] = generate_secret_string
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if replica_regions is not None:
            self._values["replica_regions"] = replica_regions
        if secret_name is not None:
            self._values["secret_name"] = secret_name
        if convert_to_json is not None:
            self._values["convert_to_json"] = convert_to_json
        if flatten is not None:
            self._values["flatten"] = flatten
        if sops_age_key is not None:
            self._values["sops_age_key"] = sops_age_key
        if sops_file_format is not None:
            self._values["sops_file_format"] = sops_file_format
        if sops_kms_key is not None:
            self._values["sops_kms_key"] = sops_kms_key
        if sops_provider is not None:
            self._values["sops_provider"] = sops_provider
        if stringify_values is not None:
            self._values["stringify_values"] = stringify_values
        if upload_type is not None:
            self._values["upload_type"] = upload_type

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An optional, human-friendly description of the secret.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[aws_cdk.aws_kms.IKey]:
        '''The customer-managed encryption key to use for encrypting the secret value.

        :default: - A default KMS key for the account and region is used.
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[aws_cdk.aws_kms.IKey], result)

    @builtins.property
    def generate_secret_string(
        self,
    ) -> typing.Optional[aws_cdk.aws_secretsmanager.SecretStringGenerator]:
        '''Configuration for how to generate a secret value.

        :default:

        - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each
        category), per the default values of ``SecretStringGenerator``.
        '''
        result = self._values.get("generate_secret_string")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.SecretStringGenerator], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''Policy to apply when the secret is removed from this stack.

        :default: - Not set.
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def replica_regions(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_secretsmanager.ReplicaRegion]]:
        '''A list of regions where to replicate this secret.

        :default: - Secret is not replicated
        '''
        result = self._values.get("replica_regions")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_secretsmanager.ReplicaRegion]], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''A name for the secret.

        Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to
        30 days blackout period. During that period, it is not possible to create another secret that shares the same name.

        :default: - A name is generated by CloudFormation.
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sops_file_path(self) -> builtins.str:
        '''(experimental) The filepath to the sops file.

        :stability: experimental
        '''
        result = self._values.get("sops_file_path")
        assert result is not None, "Required property 'sops_file_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def convert_to_json(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the encrypted sops value should be converted to JSON?

        Only JSON can be handled by cloud formations dynamic references.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("convert_to_json")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def flatten(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Should the structure be flattened?

        The result will be a flat structure and all
        object keys will be replaced with the full jsonpath as key.
        This is usefull for dynamic references, as those don't support nested objects.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("flatten")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def sops_age_key(self) -> typing.Optional[aws_cdk.SecretValue]:
        '''(experimental) The age key that should be used for encryption.

        :stability: experimental
        '''
        result = self._values.get("sops_age_key")
        return typing.cast(typing.Optional[aws_cdk.SecretValue], result)

    @builtins.property
    def sops_file_format(self) -> typing.Optional[builtins.str]:
        '''(experimental) The format of the sops file.

        :default: - The fileformat will be derived from the file ending

        :stability: experimental
        '''
        result = self._values.get("sops_file_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sops_kms_key(self) -> typing.Optional[typing.List[aws_cdk.aws_kms.IKey]]:
        '''(experimental) The kmsKey used to encrypt the sops file.

        Encrypt permissions
        will be granted to the custom resource provider.

        :default: - The key will be derived from the sops file

        :stability: experimental
        '''
        result = self._values.get("sops_kms_key")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_kms.IKey]], result)

    @builtins.property
    def sops_provider(self) -> typing.Optional[SopsSyncProvider]:
        '''(experimental) The custom resource provider to use.

        If you don't specify any, a new
        provider will be created - or if already exists within this stack - reused.

        :default: - A new singleton provider will be created

        :stability: experimental
        '''
        result = self._values.get("sops_provider")
        return typing.cast(typing.Optional[SopsSyncProvider], result)

    @builtins.property
    def stringify_values(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Shall all values be flattened?

        This is usefull for dynamic references, as there
        are lookup errors for certain float types

        :stability: experimental
        '''
        result = self._values.get("stringify_values")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def upload_type(self) -> typing.Optional[UploadType]:
        '''(experimental) How should the secret be passed to the CustomResource?

        :default: INLINE

        :stability: experimental
        '''
        result = self._values.get("upload_type")
        return typing.cast(typing.Optional[UploadType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SopsSecretProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SopsSecret",
    "SopsSecretProps",
    "SopsSync",
    "SopsSyncOptions",
    "SopsSyncProps",
    "SopsSyncProvider",
    "UploadType",
]

publication.publish()
