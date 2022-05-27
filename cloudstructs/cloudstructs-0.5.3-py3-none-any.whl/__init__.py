'''
# cloudstructs

High-level constructs for AWS CDK

## Installation

`npm install cloudstructs` or `yarn add cloudstructs`

Version >= 0.2.0 requires AWS CDK v2.

## Constructs

* [`CodeCommitMirror`](src/codecommit-mirror) Mirror a repository to AWS CodeCommit on schedule
* [`EcsServiceRoller`](src/ecs-service-roller) Roll your ECS service tasks on schedule or with
  a rule
* [`EmailReceiver`](src/email-receiver) Receive emails through SES, save them to S3
  and invoke a Lambda function
* [`SlackApp`](src/slack-app) Deploy Slack apps from manifests
* [`SlackEvents`](src/slack-events) Send Slack events to Amazon EventBridge
* [`SlackTextract`](src/slack-textract) Extract text from images posted to Slack
  using Amazon Textract. The extracted text is posted in a thread under the image
  and gets indexed!
* [`StateMachineCustomResourceProvider`](src/state-machine-cr-provider) Implement custom
  resources with AWS Step Functions state machines
* [`StaticWebsite`](src/static-website) A CloudFront static website hosted on S3 with
  HTTPS redirect, SPA redirect, HTTP security headers and backend configuration saved
  to the bucket.
* [`ToolkitCleaner`](src/toolkit-cleaner) Clean unused S3 and ECR assets from your CDK
  Toolkit.
* [`UrlShortener`](src/url-shortener) Deploy an URL shortener API
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
import aws_cdk.aws_apigateway
import aws_cdk.aws_cloudfront
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_route53
import aws_cdk.aws_s3
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_ses
import constructs


class CodeCommitMirror(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.CodeCommitMirror",
):
    '''Mirror a repository to AWS CodeCommit on schedule.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        repository: "CodeCommitMirrorSourceRepository",
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: The ECS cluster where to run the mirroring operation.
        :param repository: The source repository.
        :param schedule: The schedule for the mirroring operation. Default: - everyday at midnight
        :param subnet_selection: Where to run the mirroring Fargate tasks. Default: - public subnets
        '''
        props = CodeCommitMirrorProps(
            cluster=cluster,
            repository=repository,
            schedule=schedule,
            subnet_selection=subnet_selection,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.CodeCommitMirrorProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "repository": "repository",
        "schedule": "schedule",
        "subnet_selection": "subnetSelection",
    },
)
class CodeCommitMirrorProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        repository: "CodeCommitMirrorSourceRepository",
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
    ) -> None:
        '''Properties for a CodeCommitMirror.

        :param cluster: The ECS cluster where to run the mirroring operation.
        :param repository: The source repository.
        :param schedule: The schedule for the mirroring operation. Default: - everyday at midnight
        :param subnet_selection: Where to run the mirroring Fargate tasks. Default: - public subnets
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = aws_cdk.aws_ec2.SubnetSelection(**subnet_selection)
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "repository": repository,
        }
        if schedule is not None:
            self._values["schedule"] = schedule
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection

    @builtins.property
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        '''The ECS cluster where to run the mirroring operation.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_ecs.ICluster, result)

    @builtins.property
    def repository(self) -> "CodeCommitMirrorSourceRepository":
        '''The source repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast("CodeCommitMirrorSourceRepository", result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''The schedule for the mirroring operation.

        :default: - everyday at midnight
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    @builtins.property
    def subnet_selection(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''Where to run the mirroring Fargate tasks.

        :default: - public subnets
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitMirrorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeCommitMirrorSourceRepository(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cloudstructs.CodeCommitMirrorSourceRepository",
):
    '''A source repository for AWS CodeCommit mirroring.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="gitHub") # type: ignore[misc]
    @builtins.classmethod
    def git_hub(
        cls,
        owner: builtins.str,
        name: builtins.str,
    ) -> "CodeCommitMirrorSourceRepository":
        '''Public GitHub repository.

        :param owner: -
        :param name: -
        '''
        return typing.cast("CodeCommitMirrorSourceRepository", jsii.sinvoke(cls, "gitHub", [owner, name]))

    @jsii.member(jsii_name="private") # type: ignore[misc]
    @builtins.classmethod
    def private(
        cls,
        name: builtins.str,
        url: aws_cdk.aws_ecs.Secret,
    ) -> "CodeCommitMirrorSourceRepository":
        '''Private repository with HTTPS clone URL stored in a AWS Secrets Manager secret or a AWS Systems Manager secure string parameter.

        :param name: the repository name.
        :param url: the secret containing the HTTPS clone URL.
        '''
        return typing.cast("CodeCommitMirrorSourceRepository", jsii.sinvoke(cls, "private", [name, url]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plainTextUrl")
    @abc.abstractmethod
    def plain_text_url(self) -> typing.Optional[builtins.str]:
        '''The HTTPS clone URL in plain text, used for a public repository.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretUrl")
    @abc.abstractmethod
    def secret_url(self) -> typing.Optional[aws_cdk.aws_ecs.Secret]:
        '''The HTTPS clone URL if the repository is private.

        The secret should contain the username and/or token.

        Example::

            `https://TOKEN@github.com/owner/name`
            `https://USERNAME:TOKEN@bitbucket.org/owner/name.git`
        '''
        ...


class _CodeCommitMirrorSourceRepositoryProxy(CodeCommitMirrorSourceRepository):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="plainTextUrl")
    def plain_text_url(self) -> typing.Optional[builtins.str]:
        '''The HTTPS clone URL in plain text, used for a public repository.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "plainTextUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretUrl")
    def secret_url(self) -> typing.Optional[aws_cdk.aws_ecs.Secret]:
        '''The HTTPS clone URL if the repository is private.

        The secret should contain the username and/or token.

        Example::

            `https://TOKEN@github.com/owner/name`
            `https://USERNAME:TOKEN@bitbucket.org/owner/name.git`
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.Secret], jsii.get(self, "secretUrl"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, CodeCommitMirrorSourceRepository).__jsii_proxy_class__ = lambda : _CodeCommitMirrorSourceRepositoryProxy


class EcsServiceRoller(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.EcsServiceRoller",
):
    '''Roll your ECS service tasks on schedule or with a rule.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        service: aws_cdk.aws_ecs.IService,
        trigger: typing.Optional["RollTrigger"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: The ECS cluster where the services run.
        :param service: The ECS service for which tasks should be rolled.
        :param trigger: The rule or schedule that should trigger a roll. Default: - roll everyday at midnight
        '''
        props = EcsServiceRollerProps(
            cluster=cluster, service=service, trigger=trigger
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.EcsServiceRollerProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster", "service": "service", "trigger": "trigger"},
)
class EcsServiceRollerProps:
    def __init__(
        self,
        *,
        cluster: aws_cdk.aws_ecs.ICluster,
        service: aws_cdk.aws_ecs.IService,
        trigger: typing.Optional["RollTrigger"] = None,
    ) -> None:
        '''Properties for a EcsServiceRoller.

        :param cluster: The ECS cluster where the services run.
        :param service: The ECS service for which tasks should be rolled.
        :param trigger: The rule or schedule that should trigger a roll. Default: - roll everyday at midnight
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cluster": cluster,
            "service": service,
        }
        if trigger is not None:
            self._values["trigger"] = trigger

    @builtins.property
    def cluster(self) -> aws_cdk.aws_ecs.ICluster:
        '''The ECS cluster where the services run.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(aws_cdk.aws_ecs.ICluster, result)

    @builtins.property
    def service(self) -> aws_cdk.aws_ecs.IService:
        '''The ECS service for which tasks should be rolled.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(aws_cdk.aws_ecs.IService, result)

    @builtins.property
    def trigger(self) -> typing.Optional["RollTrigger"]:
        '''The rule or schedule that should trigger a roll.

        :default: - roll everyday at midnight
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional["RollTrigger"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsServiceRollerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmailReceiver(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.EmailReceiver",
):
    '''Receive emails through SES, save them to S3 and invokes a Lambda function.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        function: aws_cdk.aws_lambda.IFunction,
        receipt_rule_set: aws_cdk.aws_ses.IReceiptRuleSet,
        recipients: typing.Sequence[builtins.str],
        after_rule: typing.Optional[aws_cdk.aws_ses.IReceiptRule] = None,
        source_whitelist: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param function: A Lambda function to invoke after the message is saved to S3. The Lambda function will be invoked with a SESMessage as event.
        :param receipt_rule_set: The SES receipt rule set where a receipt rule will be added.
        :param recipients: The recipients for which emails should be received.
        :param after_rule: An existing rule after which the new rule will be placed in the rule set. Default: - The new rule is inserted at the beginning of the rule list.
        :param source_whitelist: A regular expression to whitelist source email addresses. Default: - no whitelisting of source email addresses
        '''
        props = EmailReceiverProps(
            function=function,
            receipt_rule_set=receipt_rule_set,
            recipients=recipients,
            after_rule=after_rule,
            source_whitelist=source_whitelist,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.EmailReceiverProps",
    jsii_struct_bases=[],
    name_mapping={
        "function": "function",
        "receipt_rule_set": "receiptRuleSet",
        "recipients": "recipients",
        "after_rule": "afterRule",
        "source_whitelist": "sourceWhitelist",
    },
)
class EmailReceiverProps:
    def __init__(
        self,
        *,
        function: aws_cdk.aws_lambda.IFunction,
        receipt_rule_set: aws_cdk.aws_ses.IReceiptRuleSet,
        recipients: typing.Sequence[builtins.str],
        after_rule: typing.Optional[aws_cdk.aws_ses.IReceiptRule] = None,
        source_whitelist: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for an EmailReceiver.

        :param function: A Lambda function to invoke after the message is saved to S3. The Lambda function will be invoked with a SESMessage as event.
        :param receipt_rule_set: The SES receipt rule set where a receipt rule will be added.
        :param recipients: The recipients for which emails should be received.
        :param after_rule: An existing rule after which the new rule will be placed in the rule set. Default: - The new rule is inserted at the beginning of the rule list.
        :param source_whitelist: A regular expression to whitelist source email addresses. Default: - no whitelisting of source email addresses
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "function": function,
            "receipt_rule_set": receipt_rule_set,
            "recipients": recipients,
        }
        if after_rule is not None:
            self._values["after_rule"] = after_rule
        if source_whitelist is not None:
            self._values["source_whitelist"] = source_whitelist

    @builtins.property
    def function(self) -> aws_cdk.aws_lambda.IFunction:
        '''A Lambda function to invoke after the message is saved to S3.

        The Lambda
        function will be invoked with a SESMessage as event.
        '''
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def receipt_rule_set(self) -> aws_cdk.aws_ses.IReceiptRuleSet:
        '''The SES receipt rule set where a receipt rule will be added.'''
        result = self._values.get("receipt_rule_set")
        assert result is not None, "Required property 'receipt_rule_set' is missing"
        return typing.cast(aws_cdk.aws_ses.IReceiptRuleSet, result)

    @builtins.property
    def recipients(self) -> typing.List[builtins.str]:
        '''The recipients for which emails should be received.'''
        result = self._values.get("recipients")
        assert result is not None, "Required property 'recipients' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def after_rule(self) -> typing.Optional[aws_cdk.aws_ses.IReceiptRule]:
        '''An existing rule after which the new rule will be placed in the rule set.

        :default: - The new rule is inserted at the beginning of the rule list.
        '''
        result = self._values.get("after_rule")
        return typing.cast(typing.Optional[aws_cdk.aws_ses.IReceiptRule], result)

    @builtins.property
    def source_whitelist(self) -> typing.Optional[builtins.str]:
        '''A regular expression to whitelist source email addresses.

        :default: - no whitelisting of source email addresses
        '''
        result = self._values.get("source_whitelist")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailReceiverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cloudstructs.IStateMachine")
class IStateMachine(typing_extensions.Protocol):
    '''A State Machine.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.'''
        ...


class _IStateMachineProxy:
    '''A State Machine.'''

    __jsii_type__: typing.ClassVar[str] = "cloudstructs.IStateMachine"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.'''
        return typing.cast(builtins.str, jsii.get(self, "stateMachineArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStateMachine).__jsii_proxy_class__ = lambda : _IStateMachineProxy


class RollTrigger(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cloudstructs.RollTrigger",
):
    '''The rule or schedule that should trigger a roll.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromRule") # type: ignore[misc]
    @builtins.classmethod
    def from_rule(cls, rule: aws_cdk.aws_events.Rule) -> "RollTrigger":
        '''Rule that should trigger a roll.

        :param rule: -
        '''
        return typing.cast("RollTrigger", jsii.sinvoke(cls, "fromRule", [rule]))

    @jsii.member(jsii_name="fromSchedule") # type: ignore[misc]
    @builtins.classmethod
    def from_schedule(cls, schedule: aws_cdk.aws_events.Schedule) -> "RollTrigger":
        '''Schedule that should trigger a roll.

        :param schedule: -
        '''
        return typing.cast("RollTrigger", jsii.sinvoke(cls, "fromSchedule", [schedule]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    @abc.abstractmethod
    def rule(self) -> typing.Optional[aws_cdk.aws_events.Rule]:
        '''Roll rule.

        :default: - roll everyday at midnight
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    @abc.abstractmethod
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''Roll schedule.

        :default: - roll everyday at midnight
        '''
        ...


class _RollTriggerProxy(RollTrigger):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.Optional[aws_cdk.aws_events.Rule]:
        '''Roll rule.

        :default: - roll everyday at midnight
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_events.Rule], jsii.get(self, "rule"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''Roll schedule.

        :default: - roll everyday at midnight
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], jsii.get(self, "schedule"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RollTrigger).__jsii_proxy_class__ = lambda : _RollTriggerProxy


class SamlFederatedPrincipal(
    aws_cdk.aws_iam.FederatedPrincipal,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SamlFederatedPrincipal",
):
    '''(deprecated) Principal entity that represents a SAML federated identity provider.

    :deprecated: use ``SamlPrincipal`` from ``aws-cdk-lib/aws-iam``

    :stability: deprecated
    '''

    def __init__(self, identity_provider: "SamlIdentityProvider") -> None:
        '''
        :param identity_provider: -

        :stability: deprecated
        '''
        jsii.create(self.__class__, self, [identity_provider])


class SamlIdentityProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SamlIdentityProvider",
):
    '''(deprecated) Create a SAML identity provider.

    :deprecated: use ``SamlProvider`` from ``aws-cdk-lib/aws-iam``

    :stability: deprecated
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        metadata_document: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param metadata_document: (deprecated) An XML document generated by an identity provider (IdP) that supports SAML 2.0. The document includes the issuer's name, expiration information, and keys that can be used to validate the SAML authentication response (assertions) that are received from the IdP. You must generate the metadata document using the identity management software that is used as your organization's IdP.
        :param name: (deprecated) A name for the SAML identity provider. Default: - derived for the node's unique id

        :stability: deprecated
        '''
        props = SamlIdentityProviderProps(
            metadata_document=metadata_document, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="samlIdentityProviderArn")
    def saml_identity_provider_arn(self) -> builtins.str:
        '''(deprecated) The ARN of the SAML identity provider.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "samlIdentityProviderArn"))


@jsii.data_type(
    jsii_type="cloudstructs.SamlIdentityProviderProps",
    jsii_struct_bases=[],
    name_mapping={"metadata_document": "metadataDocument", "name": "name"},
)
class SamlIdentityProviderProps:
    def __init__(
        self,
        *,
        metadata_document: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(deprecated) Properties for a SamlProvider.

        :param metadata_document: (deprecated) An XML document generated by an identity provider (IdP) that supports SAML 2.0. The document includes the issuer's name, expiration information, and keys that can be used to validate the SAML authentication response (assertions) that are received from the IdP. You must generate the metadata document using the identity management software that is used as your organization's IdP.
        :param name: (deprecated) A name for the SAML identity provider. Default: - derived for the node's unique id

        :deprecated: use ``SamlProviderProps`` from ``aws-cdk-lib/aws-iam``

        :stability: deprecated
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "metadata_document": metadata_document,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def metadata_document(self) -> builtins.str:
        '''(deprecated) An XML document generated by an identity provider (IdP) that supports SAML 2.0.

        The document includes the issuer's name, expiration information, and keys that
        can be used to validate the SAML authentication response (assertions) that are
        received from the IdP. You must generate the metadata document using the identity
        management software that is used as your organization's IdP.

        :stability: deprecated
        '''
        result = self._values.get("metadata_document")
        assert result is not None, "Required property 'metadata_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) A name for the SAML identity provider.

        :default: - derived for the node's unique id

        :stability: deprecated
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SamlIdentityProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackApp(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackApp",
):
    '''A Slack application deployed with a manifest.

    :see: https://api.slack.com/reference/manifests
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        configuration_token_secret: aws_cdk.aws_secretsmanager.ISecret,
        manifest: "SlackAppManifestDefinition",
        credentials_secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param configuration_token_secret: An AWS Secrets Manager secret containing the app configuration token. Must use the following JSON format:: { "refreshToken": "<token>" }
        :param manifest: The definition of the app manifest.
        :param credentials_secret: The AWS Secrets Manager secret where to store the app credentials. Default: - a new secret is created
        '''
        props = SlackAppProps(
            configuration_token_secret=configuration_token_secret,
            manifest=manifest,
            credentials_secret=credentials_secret,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''The ID of the application.'''
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        '''A dynamic reference to the client ID of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        '''A dynamic reference to the client secret of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''An AWS Secrets Manager secret containing the credentials of the application.

        Example::

           {
              "appId": "...",
              "clientId": "...",
              "clientSecret": "...",
              "verificationToken": "...",
              "signingSecret": "..."
           }
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "credentials"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signingSecret")
    def signing_secret(self) -> builtins.str:
        '''A dynamic reference to the signing secret of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "signingSecret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verificationToken")
    def verification_token(self) -> builtins.str:
        '''A dynamic reference to the verification token of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "verificationToken"))


class SlackAppManifest(
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackAppManifest",
):
    '''A Slack app manifest.

    :see: https://api.slack.com/reference/manifests
    '''

    def __init__(
        self,
        *,
        name: builtins.str,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_home: typing.Optional["SlackAppManifestAppHome"] = None,
        background_color: typing.Optional[builtins.str] = None,
        bot_user: typing.Optional["SlackkAppManifestBotUser"] = None,
        description: typing.Optional[builtins.str] = None,
        event_subscriptions: typing.Optional["SlackAppManifestEventSubscriptions"] = None,
        interactivity: typing.Optional["SlackAppManifestInteractivity"] = None,
        long_description: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        minor_version: typing.Optional[jsii.Number] = None,
        oauth_config: typing.Optional["SlackAppManifestOauthConfig"] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        shortcuts: typing.Optional[typing.Sequence["SlackAppManifestShortcut"]] = None,
        slash_commands: typing.Optional[typing.Sequence["SlackAppManifestSlashCommand"]] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
        unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_steps: typing.Optional[typing.Sequence["SlackAppManifestWorkflowStep"]] = None,
    ) -> None:
        '''
        :param name: The name of the app. Maximum length is 35 characters.
        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param app_home: App Home configuration.
        :param background_color: A hex color value that specifies the background color used on hovercards that display information about your app. Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        :param bot_user: Bot user configuration.
        :param description: A short description of the app for display to users. Maximum length is 140 characters. Default: - no short description
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param long_description: A longer version of the description of the app. Maximum length is 4000 characters.
        :param major_version: The major version of the manifest schema to target. Default: - do not target a specific major version
        :param minor_version: The minor version of the manifest schema to target. Default: - do not target a specific minor version
        :param oauth_config: OAuth configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param shortcuts: Shortcuts configuration. A maximum of 5 shortcuts can be included.
        :param slash_commands: Slash commands configuration. A maximum of 5 slash commands can be included.
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        :param unfurl_domains: Valid unfurl domains to register. A maximum of 5 unfurl domains can be included.
        :param workflow_steps: Workflow steps. A maximum of 10 workflow steps can be included.
        '''
        props = SlackAppManifestProps(
            name=name,
            allowed_ip_address_ranges=allowed_ip_address_ranges,
            app_home=app_home,
            background_color=background_color,
            bot_user=bot_user,
            description=description,
            event_subscriptions=event_subscriptions,
            interactivity=interactivity,
            long_description=long_description,
            major_version=major_version,
            minor_version=minor_version,
            oauth_config=oauth_config,
            org_deploy=org_deploy,
            shortcuts=shortcuts,
            slash_commands=slash_commands,
            socket_mode=socket_mode,
            unfurl_domains=unfurl_domains,
            workflow_steps=workflow_steps,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self, construct: constructs.IConstruct) -> builtins.str:
        '''
        :param construct: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "render", [construct]))


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestAppHome",
    jsii_struct_bases=[],
    name_mapping={
        "home_tab": "homeTab",
        "messages_tab": "messagesTab",
        "messages_tab_read_only": "messagesTabReadOnly",
    },
)
class SlackAppManifestAppHome:
    def __init__(
        self,
        *,
        home_tab: typing.Optional[builtins.bool] = None,
        messages_tab: typing.Optional[builtins.bool] = None,
        messages_tab_read_only: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''App Home configuration.

        :param home_tab: Wether the Home tab is enabled. Default: false
        :param messages_tab: Wether the Messages is enabled. Default: false
        :param messages_tab_read_only: Whether the users can send messages to your app in the Messages tab of your App Home. Default: false

        :see: https://api.slack.com/surfaces/tabs
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if home_tab is not None:
            self._values["home_tab"] = home_tab
        if messages_tab is not None:
            self._values["messages_tab"] = messages_tab
        if messages_tab_read_only is not None:
            self._values["messages_tab_read_only"] = messages_tab_read_only

    @builtins.property
    def home_tab(self) -> typing.Optional[builtins.bool]:
        '''Wether the Home tab is enabled.

        :default: false
        '''
        result = self._values.get("home_tab")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def messages_tab(self) -> typing.Optional[builtins.bool]:
        '''Wether the Messages is enabled.

        :default: false
        '''
        result = self._values.get("messages_tab")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def messages_tab_read_only(self) -> typing.Optional[builtins.bool]:
        '''Whether the users can send messages to your app in the Messages tab of your App Home.

        :default: false
        '''
        result = self._values.get("messages_tab_read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestAppHome(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackAppManifestDefinition(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cloudstructs.SlackAppManifestDefinition",
):
    '''A Slack app manifest definition.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFile") # type: ignore[misc]
    @builtins.classmethod
    def from_file(cls, file: builtins.str) -> "SlackAppManifestDefinition":
        '''Creates a Slack app manifest from a file containg a JSON app manifest.

        :param file: -
        '''
        return typing.cast("SlackAppManifestDefinition", jsii.sinvoke(cls, "fromFile", [file]))

    @jsii.member(jsii_name="fromManifest") # type: ignore[misc]
    @builtins.classmethod
    def from_manifest(
        cls,
        *,
        name: builtins.str,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_home: typing.Optional[SlackAppManifestAppHome] = None,
        background_color: typing.Optional[builtins.str] = None,
        bot_user: typing.Optional["SlackkAppManifestBotUser"] = None,
        description: typing.Optional[builtins.str] = None,
        event_subscriptions: typing.Optional["SlackAppManifestEventSubscriptions"] = None,
        interactivity: typing.Optional["SlackAppManifestInteractivity"] = None,
        long_description: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        minor_version: typing.Optional[jsii.Number] = None,
        oauth_config: typing.Optional["SlackAppManifestOauthConfig"] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        shortcuts: typing.Optional[typing.Sequence["SlackAppManifestShortcut"]] = None,
        slash_commands: typing.Optional[typing.Sequence["SlackAppManifestSlashCommand"]] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
        unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_steps: typing.Optional[typing.Sequence["SlackAppManifestWorkflowStep"]] = None,
    ) -> "SlackAppManifestDefinition":
        '''Creates a Slack app manifest by specifying properties.

        :param name: The name of the app. Maximum length is 35 characters.
        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param app_home: App Home configuration.
        :param background_color: A hex color value that specifies the background color used on hovercards that display information about your app. Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        :param bot_user: Bot user configuration.
        :param description: A short description of the app for display to users. Maximum length is 140 characters. Default: - no short description
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param long_description: A longer version of the description of the app. Maximum length is 4000 characters.
        :param major_version: The major version of the manifest schema to target. Default: - do not target a specific major version
        :param minor_version: The minor version of the manifest schema to target. Default: - do not target a specific minor version
        :param oauth_config: OAuth configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param shortcuts: Shortcuts configuration. A maximum of 5 shortcuts can be included.
        :param slash_commands: Slash commands configuration. A maximum of 5 slash commands can be included.
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        :param unfurl_domains: Valid unfurl domains to register. A maximum of 5 unfurl domains can be included.
        :param workflow_steps: Workflow steps. A maximum of 10 workflow steps can be included.
        '''
        props = SlackAppManifestProps(
            name=name,
            allowed_ip_address_ranges=allowed_ip_address_ranges,
            app_home=app_home,
            background_color=background_color,
            bot_user=bot_user,
            description=description,
            event_subscriptions=event_subscriptions,
            interactivity=interactivity,
            long_description=long_description,
            major_version=major_version,
            minor_version=minor_version,
            oauth_config=oauth_config,
            org_deploy=org_deploy,
            shortcuts=shortcuts,
            slash_commands=slash_commands,
            socket_mode=socket_mode,
            unfurl_domains=unfurl_domains,
            workflow_steps=workflow_steps,
        )

        return typing.cast("SlackAppManifestDefinition", jsii.sinvoke(cls, "fromManifest", [props]))

    @jsii.member(jsii_name="fromString") # type: ignore[misc]
    @builtins.classmethod
    def from_string(cls, manifest: builtins.str) -> "SlackAppManifestDefinition":
        '''Create a Slack app manifest from a JSON app manifest encoded as a string.

        :param manifest: -
        '''
        return typing.cast("SlackAppManifestDefinition", jsii.sinvoke(cls, "fromString", [manifest]))

    @jsii.member(jsii_name="render") # type: ignore[misc]
    @abc.abstractmethod
    def render(self, construct: constructs.IConstruct) -> builtins.str:
        '''Renders the JSON app manifest encoded as a string.

        :param construct: -
        '''
        ...


class _SlackAppManifestDefinitionProxy(SlackAppManifestDefinition):
    @jsii.member(jsii_name="render")
    def render(self, construct: constructs.IConstruct) -> builtins.str:
        '''Renders the JSON app manifest encoded as a string.

        :param construct: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "render", [construct]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SlackAppManifestDefinition).__jsii_proxy_class__ = lambda : _SlackAppManifestDefinitionProxy


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestEventSubscriptions",
    jsii_struct_bases=[],
    name_mapping={
        "request_url": "requestUrl",
        "bot_events": "botEvents",
        "user_events": "userEvents",
    },
)
class SlackAppManifestEventSubscriptions:
    def __init__(
        self,
        *,
        request_url: builtins.str,
        bot_events: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_events: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Events API configuration for the app.

        :param request_url: The full https URL that acts as the Events API request URL.
        :param bot_events: Event types you want the app to subscribe to. A maximum of 100 event types can be used
        :param user_events: Event types you want the app to subscribe to on behalf of authorized users. A maximum of 100 event types can be used.

        :see: https://api.slack.com/events-api
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "request_url": request_url,
        }
        if bot_events is not None:
            self._values["bot_events"] = bot_events
        if user_events is not None:
            self._values["user_events"] = user_events

    @builtins.property
    def request_url(self) -> builtins.str:
        '''The full https URL that acts as the Events API request URL.

        :see: https://api.slack.com/events-api#the-events-api__subscribing-to-event-types__events-api-request-urls
        '''
        result = self._values.get("request_url")
        assert result is not None, "Required property 'request_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bot_events(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Event types you want the app to subscribe to.

        A maximum of 100 event types can be used

        :see: https://api.slack.com/events
        '''
        result = self._values.get("bot_events")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_events(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Event types you want the app to subscribe to on behalf of authorized users.

        A maximum of 100 event types can be used.
        '''
        result = self._values.get("user_events")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestEventSubscriptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestInteractivity",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "message_menu_options_url": "messageMenuOptionsUrl",
        "request_url": "requestUrl",
    },
)
class SlackAppManifestInteractivity:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        message_menu_options_url: typing.Optional[builtins.str] = None,
        request_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Interactivity configuration for the app.

        :param enabled: Whether or not interactivity features are enabled. Default: true
        :param message_menu_options_url: The full https URL that acts as th interactive Options Load URL.
        :param request_url: The full https URL that acts as the interactive Request URL.

        :see: https://api.slack.com/interactivity/handling#setup
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if message_menu_options_url is not None:
            self._values["message_menu_options_url"] = message_menu_options_url
        if request_url is not None:
            self._values["request_url"] = request_url

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether or not interactivity features are enabled.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def message_menu_options_url(self) -> typing.Optional[builtins.str]:
        '''The full https URL that acts as th interactive Options Load URL.'''
        result = self._values.get("message_menu_options_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_url(self) -> typing.Optional[builtins.str]:
        '''The full https URL that acts as the interactive Request URL.'''
        result = self._values.get("request_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestInteractivity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestOauthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "bot_scopes": "botScopes",
        "redirect_urls": "redirectUrls",
        "user_scopes": "userScopes",
    },
)
class SlackAppManifestOauthConfig:
    def __init__(
        self,
        *,
        bot_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        redirect_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''OAuth configuration for the app.

        :param bot_scopes: Bot scopes to request upon app installation. A maximum of 255 scopes can be included.
        :param redirect_urls: OAuth redirect URLs. A maximum of 1000 redirect URLs can be included.
        :param user_scopes: User scopes to request upon app installation. A maximum of 255 scopes can be included.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if bot_scopes is not None:
            self._values["bot_scopes"] = bot_scopes
        if redirect_urls is not None:
            self._values["redirect_urls"] = redirect_urls
        if user_scopes is not None:
            self._values["user_scopes"] = user_scopes

    @builtins.property
    def bot_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Bot scopes to request upon app installation.

        A maximum of 255 scopes can be included.

        :see: https://api.slack.com/scopes
        '''
        result = self._values.get("bot_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def redirect_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''OAuth redirect URLs.

        A maximum of 1000 redirect URLs can be included.

        :see: https://api.slack.com/authentication/oauth-v2#redirect_urls
        '''
        result = self._values.get("redirect_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''User scopes to request upon app installation.

        A maximum of 255 scopes can be included.

        :see: https://api.slack.com/scopes
        '''
        result = self._values.get("user_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestOauthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "allowed_ip_address_ranges": "allowedIpAddressRanges",
        "app_home": "appHome",
        "background_color": "backgroundColor",
        "bot_user": "botUser",
        "description": "description",
        "event_subscriptions": "eventSubscriptions",
        "interactivity": "interactivity",
        "long_description": "longDescription",
        "major_version": "majorVersion",
        "minor_version": "minorVersion",
        "oauth_config": "oauthConfig",
        "org_deploy": "orgDeploy",
        "shortcuts": "shortcuts",
        "slash_commands": "slashCommands",
        "socket_mode": "socketMode",
        "unfurl_domains": "unfurlDomains",
        "workflow_steps": "workflowSteps",
    },
)
class SlackAppManifestProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_home: typing.Optional[SlackAppManifestAppHome] = None,
        background_color: typing.Optional[builtins.str] = None,
        bot_user: typing.Optional["SlackkAppManifestBotUser"] = None,
        description: typing.Optional[builtins.str] = None,
        event_subscriptions: typing.Optional[SlackAppManifestEventSubscriptions] = None,
        interactivity: typing.Optional[SlackAppManifestInteractivity] = None,
        long_description: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        minor_version: typing.Optional[jsii.Number] = None,
        oauth_config: typing.Optional[SlackAppManifestOauthConfig] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        shortcuts: typing.Optional[typing.Sequence["SlackAppManifestShortcut"]] = None,
        slash_commands: typing.Optional[typing.Sequence["SlackAppManifestSlashCommand"]] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
        unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_steps: typing.Optional[typing.Sequence["SlackAppManifestWorkflowStep"]] = None,
    ) -> None:
        '''Properties for a Slack app manifest.

        :param name: The name of the app. Maximum length is 35 characters.
        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param app_home: App Home configuration.
        :param background_color: A hex color value that specifies the background color used on hovercards that display information about your app. Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        :param bot_user: Bot user configuration.
        :param description: A short description of the app for display to users. Maximum length is 140 characters. Default: - no short description
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param long_description: A longer version of the description of the app. Maximum length is 4000 characters.
        :param major_version: The major version of the manifest schema to target. Default: - do not target a specific major version
        :param minor_version: The minor version of the manifest schema to target. Default: - do not target a specific minor version
        :param oauth_config: OAuth configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param shortcuts: Shortcuts configuration. A maximum of 5 shortcuts can be included.
        :param slash_commands: Slash commands configuration. A maximum of 5 slash commands can be included.
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        :param unfurl_domains: Valid unfurl domains to register. A maximum of 5 unfurl domains can be included.
        :param workflow_steps: Workflow steps. A maximum of 10 workflow steps can be included.

        :see: https://api.slack.com/reference/manifests
        '''
        if isinstance(app_home, dict):
            app_home = SlackAppManifestAppHome(**app_home)
        if isinstance(bot_user, dict):
            bot_user = SlackkAppManifestBotUser(**bot_user)
        if isinstance(event_subscriptions, dict):
            event_subscriptions = SlackAppManifestEventSubscriptions(**event_subscriptions)
        if isinstance(interactivity, dict):
            interactivity = SlackAppManifestInteractivity(**interactivity)
        if isinstance(oauth_config, dict):
            oauth_config = SlackAppManifestOauthConfig(**oauth_config)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if allowed_ip_address_ranges is not None:
            self._values["allowed_ip_address_ranges"] = allowed_ip_address_ranges
        if app_home is not None:
            self._values["app_home"] = app_home
        if background_color is not None:
            self._values["background_color"] = background_color
        if bot_user is not None:
            self._values["bot_user"] = bot_user
        if description is not None:
            self._values["description"] = description
        if event_subscriptions is not None:
            self._values["event_subscriptions"] = event_subscriptions
        if interactivity is not None:
            self._values["interactivity"] = interactivity
        if long_description is not None:
            self._values["long_description"] = long_description
        if major_version is not None:
            self._values["major_version"] = major_version
        if minor_version is not None:
            self._values["minor_version"] = minor_version
        if oauth_config is not None:
            self._values["oauth_config"] = oauth_config
        if org_deploy is not None:
            self._values["org_deploy"] = org_deploy
        if shortcuts is not None:
            self._values["shortcuts"] = shortcuts
        if slash_commands is not None:
            self._values["slash_commands"] = slash_commands
        if socket_mode is not None:
            self._values["socket_mode"] = socket_mode
        if unfurl_domains is not None:
            self._values["unfurl_domains"] = unfurl_domains
        if workflow_steps is not None:
            self._values["workflow_steps"] = workflow_steps

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the app.

        Maximum length is 35 characters.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_ip_address_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of IP addresses that conform to the Allowed IP Ranges feature.

        :see: https://api.slack.com/authentication/best-practices#ip_allowlisting
        '''
        result = self._values.get("allowed_ip_address_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def app_home(self) -> typing.Optional[SlackAppManifestAppHome]:
        '''App Home configuration.

        :see: https://api.slack.com/surfaces/tabs
        '''
        result = self._values.get("app_home")
        return typing.cast(typing.Optional[SlackAppManifestAppHome], result)

    @builtins.property
    def background_color(self) -> typing.Optional[builtins.str]:
        '''A hex color value that specifies the background color used on hovercards that display information about your app.

        Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        '''
        result = self._values.get("background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bot_user(self) -> typing.Optional["SlackkAppManifestBotUser"]:
        '''Bot user configuration.

        :see: https://api.slack.com/bot-users
        '''
        result = self._values.get("bot_user")
        return typing.cast(typing.Optional["SlackkAppManifestBotUser"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A short description of the app for display to users.

        Maximum length is 140 characters.

        :default: - no short description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_subscriptions(
        self,
    ) -> typing.Optional[SlackAppManifestEventSubscriptions]:
        '''Events API configuration for the app.

        :see: https://api.slack.com/events-api
        '''
        result = self._values.get("event_subscriptions")
        return typing.cast(typing.Optional[SlackAppManifestEventSubscriptions], result)

    @builtins.property
    def interactivity(self) -> typing.Optional[SlackAppManifestInteractivity]:
        '''Interactivity configuration for the app.'''
        result = self._values.get("interactivity")
        return typing.cast(typing.Optional[SlackAppManifestInteractivity], result)

    @builtins.property
    def long_description(self) -> typing.Optional[builtins.str]:
        '''A longer version of the description of the app.

        Maximum length is 4000 characters.
        '''
        result = self._values.get("long_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''The major version of the manifest schema to target.

        :default: - do not target a specific major version
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minor_version(self) -> typing.Optional[jsii.Number]:
        '''The minor version of the manifest schema to target.

        :default: - do not target a specific minor version
        '''
        result = self._values.get("minor_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def oauth_config(self) -> typing.Optional[SlackAppManifestOauthConfig]:
        '''OAuth configuration for the app.'''
        result = self._values.get("oauth_config")
        return typing.cast(typing.Optional[SlackAppManifestOauthConfig], result)

    @builtins.property
    def org_deploy(self) -> typing.Optional[builtins.bool]:
        '''Whether org-wide deploy is enabled.

        :default: false

        :see: https://api.slack.com/enterprise/apps
        '''
        result = self._values.get("org_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def shortcuts(self) -> typing.Optional[typing.List["SlackAppManifestShortcut"]]:
        '''Shortcuts configuration.

        A maximum of 5 shortcuts can be included.

        :see: https://api.slack.com/interactivity/shortcuts
        '''
        result = self._values.get("shortcuts")
        return typing.cast(typing.Optional[typing.List["SlackAppManifestShortcut"]], result)

    @builtins.property
    def slash_commands(
        self,
    ) -> typing.Optional[typing.List["SlackAppManifestSlashCommand"]]:
        '''Slash commands configuration.

        A maximum of 5 slash commands can be included.

        :see: https://api.slack.com/interactivity/slash-commands
        '''
        result = self._values.get("slash_commands")
        return typing.cast(typing.Optional[typing.List["SlackAppManifestSlashCommand"]], result)

    @builtins.property
    def socket_mode(self) -> typing.Optional[builtins.bool]:
        '''Whether Socket Mode is enabled.

        :default: false

        :see: https://api.slack.com/apis/connections/socket
        '''
        result = self._values.get("socket_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def unfurl_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Valid unfurl domains to register.

        A maximum of 5 unfurl domains can be included.

        :see: https://api.slack.com/reference/messaging/link-unfurling#configuring_domains
        '''
        result = self._values.get("unfurl_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_steps(
        self,
    ) -> typing.Optional[typing.List["SlackAppManifestWorkflowStep"]]:
        '''Workflow steps.

        A maximum of 10 workflow steps can be included.

        :see: https://api.slack.com/workflows/steps
        '''
        result = self._values.get("workflow_steps")
        return typing.cast(typing.Optional[typing.List["SlackAppManifestWorkflowStep"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestSettings",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_ip_address_ranges": "allowedIpAddressRanges",
        "event_subscriptions": "eventSubscriptions",
        "interactivity": "interactivity",
        "org_deploy": "orgDeploy",
        "socket_mode": "socketMode",
    },
)
class SlackAppManifestSettings:
    def __init__(
        self,
        *,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_subscriptions: typing.Optional[SlackAppManifestEventSubscriptions] = None,
        interactivity: typing.Optional[SlackAppManifestInteractivity] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Settings section of the app config pages.

        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        '''
        if isinstance(event_subscriptions, dict):
            event_subscriptions = SlackAppManifestEventSubscriptions(**event_subscriptions)
        if isinstance(interactivity, dict):
            interactivity = SlackAppManifestInteractivity(**interactivity)
        self._values: typing.Dict[str, typing.Any] = {}
        if allowed_ip_address_ranges is not None:
            self._values["allowed_ip_address_ranges"] = allowed_ip_address_ranges
        if event_subscriptions is not None:
            self._values["event_subscriptions"] = event_subscriptions
        if interactivity is not None:
            self._values["interactivity"] = interactivity
        if org_deploy is not None:
            self._values["org_deploy"] = org_deploy
        if socket_mode is not None:
            self._values["socket_mode"] = socket_mode

    @builtins.property
    def allowed_ip_address_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of IP addresses that conform to the Allowed IP Ranges feature.

        :see: https://api.slack.com/authentication/best-practices#ip_allowlisting
        '''
        result = self._values.get("allowed_ip_address_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def event_subscriptions(
        self,
    ) -> typing.Optional[SlackAppManifestEventSubscriptions]:
        '''Events API configuration for the app.

        :see: https://api.slack.com/events-api
        '''
        result = self._values.get("event_subscriptions")
        return typing.cast(typing.Optional[SlackAppManifestEventSubscriptions], result)

    @builtins.property
    def interactivity(self) -> typing.Optional[SlackAppManifestInteractivity]:
        '''Interactivity configuration for the app.'''
        result = self._values.get("interactivity")
        return typing.cast(typing.Optional[SlackAppManifestInteractivity], result)

    @builtins.property
    def org_deploy(self) -> typing.Optional[builtins.bool]:
        '''Whether org-wide deploy is enabled.

        :default: false

        :see: https://api.slack.com/enterprise/apps
        '''
        result = self._values.get("org_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def socket_mode(self) -> typing.Optional[builtins.bool]:
        '''Whether Socket Mode is enabled.

        :default: false

        :see: https://api.slack.com/apis/connections/socket
        '''
        result = self._values.get("socket_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestShortcut",
    jsii_struct_bases=[],
    name_mapping={
        "callback_id": "callbackId",
        "description": "description",
        "name": "name",
        "type": "type",
    },
)
class SlackAppManifestShortcut:
    def __init__(
        self,
        *,
        callback_id: builtins.str,
        description: builtins.str,
        name: builtins.str,
        type: "SlackAppManifestShortcutType",
    ) -> None:
        '''Shortcut configuration.

        :param callback_id: The callback ID of the shortcut. Maximum length is 255 characters.
        :param description: A short description of the shortcut. Maximum length is 150 characters
        :param name: The name of the shortcut.
        :param type: The type of shortcut.

        :see: https://api.slack.com/interactivity/shortcuts
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "callback_id": callback_id,
            "description": description,
            "name": name,
            "type": type,
        }

    @builtins.property
    def callback_id(self) -> builtins.str:
        '''The callback ID of the shortcut.

        Maximum length is 255 characters.
        '''
        result = self._values.get("callback_id")
        assert result is not None, "Required property 'callback_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''A short description of the shortcut.

        Maximum length is 150 characters
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the shortcut.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> "SlackAppManifestShortcutType":
        '''The type of shortcut.

        :see: https://api.slack.com/interactivity/shortcuts
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("SlackAppManifestShortcutType", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestShortcut(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cloudstructs.SlackAppManifestShortcutType")
class SlackAppManifestShortcutType(enum.Enum):
    '''Type of shortcuts.

    :see: https://api.slack.com/interactivity/shortcuts
    '''

    MESSAGE = "MESSAGE"
    '''Message shortcuts are shown to users in the context menus of messages within Slack.

    :see: https://api.slack.com/interactivity/shortcuts/using#message_shortcuts
    '''
    GLOBAL = "GLOBAL"
    '''Global shortcuts are available to users via the shortcuts button in the composer, and when using search in Slack.

    :see: https://api.slack.com/interactivity/shortcuts/using#global_shortcuts
    '''


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestSlashCommand",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "description": "description",
        "should_escape": "shouldEscape",
        "url": "url",
        "usage_hint": "usageHint",
    },
)
class SlackAppManifestSlashCommand:
    def __init__(
        self,
        *,
        command: builtins.str,
        description: builtins.str,
        should_escape: typing.Optional[builtins.bool] = None,
        url: typing.Optional[builtins.str] = None,
        usage_hint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Slash command configuration.

        :param command: The actual slash command. Maximum length is 32 characters
        :param description: The description of the slash command. Maximum length is 2000 characters.
        :param should_escape: Whether channels, users, and links typed with the slash command should be escaped. Default: false
        :param url: The full https URL that acts as the slash command's request URL.
        :param usage_hint: The short usage hint about the slash command for users. Maximum length is 1000 characters.

        :see: https://api.slack.com/interactivity/slash-commands
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "command": command,
            "description": description,
        }
        if should_escape is not None:
            self._values["should_escape"] = should_escape
        if url is not None:
            self._values["url"] = url
        if usage_hint is not None:
            self._values["usage_hint"] = usage_hint

    @builtins.property
    def command(self) -> builtins.str:
        '''The actual slash command.

        Maximum length is 32 characters
        '''
        result = self._values.get("command")
        assert result is not None, "Required property 'command' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''The description of the slash command.

        Maximum length is 2000 characters.
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def should_escape(self) -> typing.Optional[builtins.bool]:
        '''Whether channels, users, and links typed with the slash command should be escaped.

        :default: false
        '''
        result = self._values.get("should_escape")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''The full https URL that acts as the slash command's request URL.

        :see: https://api.slack.com/interactivity/slash-commands#creating_commands
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usage_hint(self) -> typing.Optional[builtins.str]:
        '''The short usage hint about the slash command for users.

        Maximum length is 1000 characters.
        '''
        result = self._values.get("usage_hint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestSlashCommand(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestWorkflowStep",
    jsii_struct_bases=[],
    name_mapping={"callback_id": "callbackId", "name": "name"},
)
class SlackAppManifestWorkflowStep:
    def __init__(self, *, callback_id: builtins.str, name: builtins.str) -> None:
        '''Workflow step.

        :param callback_id: The callback ID of the workflow step. Maximum length of 50 characters.
        :param name: The name of the workflow step. Maximum length of 50 characters.

        :see: https://api.slack.com/workflows/steps
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "callback_id": callback_id,
            "name": name,
        }

    @builtins.property
    def callback_id(self) -> builtins.str:
        '''The callback ID of the workflow step.

        Maximum length of 50 characters.
        '''
        result = self._values.get("callback_id")
        assert result is not None, "Required property 'callback_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the workflow step.

        Maximum length of 50 characters.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestWorkflowStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppProps",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_token_secret": "configurationTokenSecret",
        "manifest": "manifest",
        "credentials_secret": "credentialsSecret",
    },
)
class SlackAppProps:
    def __init__(
        self,
        *,
        configuration_token_secret: aws_cdk.aws_secretsmanager.ISecret,
        manifest: SlackAppManifestDefinition,
        credentials_secret: typing.Optional[aws_cdk.aws_secretsmanager.ISecret] = None,
    ) -> None:
        '''Properties for a SlackApp.

        :param configuration_token_secret: An AWS Secrets Manager secret containing the app configuration token. Must use the following JSON format:: { "refreshToken": "<token>" }
        :param manifest: The definition of the app manifest.
        :param credentials_secret: The AWS Secrets Manager secret where to store the app credentials. Default: - a new secret is created
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "configuration_token_secret": configuration_token_secret,
            "manifest": manifest,
        }
        if credentials_secret is not None:
            self._values["credentials_secret"] = credentials_secret

    @builtins.property
    def configuration_token_secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        '''An AWS Secrets Manager secret containing the app configuration token.

        Must use the following JSON format::

           {
              "refreshToken": "<token>"
           }
        '''
        result = self._values.get("configuration_token_secret")
        assert result is not None, "Required property 'configuration_token_secret' is missing"
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, result)

    @builtins.property
    def manifest(self) -> SlackAppManifestDefinition:
        '''The definition of the app manifest.

        :see: https://api.slack.com/reference/manifests
        '''
        result = self._values.get("manifest")
        assert result is not None, "Required property 'manifest' is missing"
        return typing.cast(SlackAppManifestDefinition, result)

    @builtins.property
    def credentials_secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''The AWS Secrets Manager secret where to store the app credentials.

        :default: - a new secret is created
        '''
        result = self._values.get("credentials_secret")
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackEvents(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackEvents",
):
    '''Send Slack events to Amazon EventBridge.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        signing_secret: aws_cdk.SecretValue,
        api_name: typing.Optional[builtins.str] = None,
        custom_event_bus: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param signing_secret: The signing secret of the Slack app.
        :param api_name: A name for the API Gateway resource. Default: SlackEventsApi
        :param custom_event_bus: Whether to use a custom event bus. Default: false
        '''
        props = SlackEventsProps(
            signing_secret=signing_secret,
            api_name=api_name,
            custom_event_bus=custom_event_bus,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eventBus")
    def event_bus(self) -> typing.Optional[aws_cdk.aws_events.EventBus]:
        '''The custom event bus where Slack events are sent.'''
        return typing.cast(typing.Optional[aws_cdk.aws_events.EventBus], jsii.get(self, "eventBus"))


@jsii.data_type(
    jsii_type="cloudstructs.SlackEventsProps",
    jsii_struct_bases=[],
    name_mapping={
        "signing_secret": "signingSecret",
        "api_name": "apiName",
        "custom_event_bus": "customEventBus",
    },
)
class SlackEventsProps:
    def __init__(
        self,
        *,
        signing_secret: aws_cdk.SecretValue,
        api_name: typing.Optional[builtins.str] = None,
        custom_event_bus: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for a SlackEvents.

        :param signing_secret: The signing secret of the Slack app.
        :param api_name: A name for the API Gateway resource. Default: SlackEventsApi
        :param custom_event_bus: Whether to use a custom event bus. Default: false
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "signing_secret": signing_secret,
        }
        if api_name is not None:
            self._values["api_name"] = api_name
        if custom_event_bus is not None:
            self._values["custom_event_bus"] = custom_event_bus

    @builtins.property
    def signing_secret(self) -> aws_cdk.SecretValue:
        '''The signing secret of the Slack app.'''
        result = self._values.get("signing_secret")
        assert result is not None, "Required property 'signing_secret' is missing"
        return typing.cast(aws_cdk.SecretValue, result)

    @builtins.property
    def api_name(self) -> typing.Optional[builtins.str]:
        '''A name for the API Gateway resource.

        :default: SlackEventsApi
        '''
        result = self._values.get("api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_event_bus(self) -> typing.Optional[builtins.bool]:
        '''Whether to use a custom event bus.

        :default: false
        '''
        result = self._values.get("custom_event_bus")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackEventsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackTextract(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackTextract",
):
    '''Extract text from images posted to Slack using Amazon Textract.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        bot_token: aws_cdk.SecretValue,
        signing_secret: aws_cdk.SecretValue,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_id: The application id of the Slack app.
        :param bot_token: The **bot** token of the Slack app. The following scopes are required: ``chat:write`` and ``files:read``
        :param signing_secret: The signing secret of the Slack app.
        '''
        props = SlackTextractProps(
            app_id=app_id, bot_token=bot_token, signing_secret=signing_secret
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.SlackTextractProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_id": "appId",
        "bot_token": "botToken",
        "signing_secret": "signingSecret",
    },
)
class SlackTextractProps:
    def __init__(
        self,
        *,
        app_id: builtins.str,
        bot_token: aws_cdk.SecretValue,
        signing_secret: aws_cdk.SecretValue,
    ) -> None:
        '''Properties for a SlackTextract.

        :param app_id: The application id of the Slack app.
        :param bot_token: The **bot** token of the Slack app. The following scopes are required: ``chat:write`` and ``files:read``
        :param signing_secret: The signing secret of the Slack app.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "app_id": app_id,
            "bot_token": bot_token,
            "signing_secret": signing_secret,
        }

    @builtins.property
    def app_id(self) -> builtins.str:
        '''The application id of the Slack app.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bot_token(self) -> aws_cdk.SecretValue:
        '''The **bot** token of the Slack app.

        The following scopes are required: ``chat:write`` and ``files:read``
        '''
        result = self._values.get("bot_token")
        assert result is not None, "Required property 'bot_token' is missing"
        return typing.cast(aws_cdk.SecretValue, result)

    @builtins.property
    def signing_secret(self) -> aws_cdk.SecretValue:
        '''The signing secret of the Slack app.'''
        result = self._values.get("signing_secret")
        assert result is not None, "Required property 'signing_secret' is missing"
        return typing.cast(aws_cdk.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackTextractProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackkAppManifestBotUser",
    jsii_struct_bases=[],
    name_mapping={"display_name": "displayName", "always_online": "alwaysOnline"},
)
class SlackkAppManifestBotUser:
    def __init__(
        self,
        *,
        display_name: builtins.str,
        always_online: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Bot user configuration.

        :param display_name: The display name of the bot user. Maximum length is 80 characters.
        :param always_online: Whether the bot user will always appear to be online. Default: false

        :see: https://api.slack.com/bot-users
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "display_name": display_name,
        }
        if always_online is not None:
            self._values["always_online"] = always_online

    @builtins.property
    def display_name(self) -> builtins.str:
        '''The display name of the bot user.

        Maximum length is 80 characters.
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def always_online(self) -> typing.Optional[builtins.bool]:
        '''Whether the bot user will always appear to be online.

        :default: false
        '''
        result = self._values.get("always_online")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackkAppManifestBotUser(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StateMachineCustomResourceProvider(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.StateMachineCustomResourceProvider",
):
    '''A state machine custom resource provider.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        state_machine: IStateMachine,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param state_machine: The state machine.
        :param timeout: Timeout. Default: Duration.minutes(30)
        '''
        props = StateMachineCustomResourceProviderProps(
            state_machine=state_machine, timeout=timeout
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''The service token.'''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))


@jsii.data_type(
    jsii_type="cloudstructs.StateMachineCustomResourceProviderProps",
    jsii_struct_bases=[],
    name_mapping={"state_machine": "stateMachine", "timeout": "timeout"},
)
class StateMachineCustomResourceProviderProps:
    def __init__(
        self,
        *,
        state_machine: IStateMachine,
        timeout: typing.Optional[aws_cdk.Duration] = None,
    ) -> None:
        '''Properties for a StateMachineCustomResourceProvider.

        :param state_machine: The state machine.
        :param timeout: Timeout. Default: Duration.minutes(30)
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "state_machine": state_machine,
        }
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def state_machine(self) -> IStateMachine:
        '''The state machine.'''
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(IStateMachine, result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''Timeout.

        :default: Duration.minutes(30)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateMachineCustomResourceProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StaticWebsite(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.StaticWebsite",
):
    '''A CloudFront static website hosted on S3.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        backend_configuration: typing.Any = None,
        redirects: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.ResponseHeadersPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: The domain name for this static website.
        :param hosted_zone: The hosted zone where records should be added.
        :param backend_configuration: A backend configuration that will be saved as ``config.json`` in the S3 bucket of the static website. The frontend can query this config by doing ``fetch('/config.json')``.
        :param redirects: A list of domain names that should redirect to ``domainName``. Default: - the domain name of the hosted zone
        :param response_headers_policy: Response headers policy for the default behavior. Default: - a new policy is created with best practice security headers
        '''
        props = StaticWebsiteProps(
            domain_name=domain_name,
            hosted_zone=hosted_zone,
            backend_configuration=backend_configuration,
            redirects=redirects,
            response_headers_policy=response_headers_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="defaultSecurityHeadersBehavior")
    def default_security_headers_behavior(
        cls,
    ) -> aws_cdk.aws_cloudfront.ResponseSecurityHeadersBehavior:
        '''Best practice security headers used as default.'''
        return typing.cast(aws_cdk.aws_cloudfront.ResponseSecurityHeadersBehavior, jsii.sget(cls, "defaultSecurityHeadersBehavior"))

    @default_security_headers_behavior.setter # type: ignore[no-redef]
    def default_security_headers_behavior(
        cls,
        value: aws_cdk.aws_cloudfront.ResponseSecurityHeadersBehavior,
    ) -> None:
        jsii.sset(cls, "defaultSecurityHeadersBehavior", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> aws_cdk.aws_s3.Bucket:
        '''The S3 bucket of this static website.'''
        return typing.cast(aws_cdk.aws_s3.Bucket, jsii.get(self, "bucket"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> aws_cdk.aws_cloudfront.Distribution:
        '''The CloudFront distribution of this static website.'''
        return typing.cast(aws_cdk.aws_cloudfront.Distribution, jsii.get(self, "distribution"))


@jsii.data_type(
    jsii_type="cloudstructs.StaticWebsiteProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "hosted_zone": "hostedZone",
        "backend_configuration": "backendConfiguration",
        "redirects": "redirects",
        "response_headers_policy": "responseHeadersPolicy",
    },
)
class StaticWebsiteProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        backend_configuration: typing.Any = None,
        redirects: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_headers_policy: typing.Optional[aws_cdk.aws_cloudfront.ResponseHeadersPolicy] = None,
    ) -> None:
        '''Properties for a StaticWebsite.

        :param domain_name: The domain name for this static website.
        :param hosted_zone: The hosted zone where records should be added.
        :param backend_configuration: A backend configuration that will be saved as ``config.json`` in the S3 bucket of the static website. The frontend can query this config by doing ``fetch('/config.json')``.
        :param redirects: A list of domain names that should redirect to ``domainName``. Default: - the domain name of the hosted zone
        :param response_headers_policy: Response headers policy for the default behavior. Default: - a new policy is created with best practice security headers
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
            "hosted_zone": hosted_zone,
        }
        if backend_configuration is not None:
            self._values["backend_configuration"] = backend_configuration
        if redirects is not None:
            self._values["redirects"] = redirects
        if response_headers_policy is not None:
            self._values["response_headers_policy"] = response_headers_policy

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The domain name for this static website.

        Example::

            www.my-static-website.com
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''The hosted zone where records should be added.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def backend_configuration(self) -> typing.Any:
        '''A backend configuration that will be saved as ``config.json`` in the S3 bucket of the static website.

        The frontend can query this config by doing ``fetch('/config.json')``.

        Example::

            { userPoolId: '1234', apiEndoint: 'https://www.my-api.com/api' }
        '''
        result = self._values.get("backend_configuration")
        return typing.cast(typing.Any, result)

    @builtins.property
    def redirects(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of domain names that should redirect to ``domainName``.

        :default: - the domain name of the hosted zone
        '''
        result = self._values.get("redirects")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def response_headers_policy(
        self,
    ) -> typing.Optional[aws_cdk.aws_cloudfront.ResponseHeadersPolicy]:
        '''Response headers policy for the default behavior.

        :default: - a new policy is created with best practice security headers
        '''
        result = self._values.get("response_headers_policy")
        return typing.cast(typing.Optional[aws_cdk.aws_cloudfront.ResponseHeadersPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticWebsiteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ToolkitCleaner(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.ToolkitCleaner",
):
    '''Clean unused S3 and ECR assets from your CDK Toolkit.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        dry_run: typing.Optional[builtins.bool] = None,
        retain_assets_newer_than: typing.Optional[aws_cdk.Duration] = None,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        schedule_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dry_run: Only output number of assets and total size that would be deleted but without actually deleting assets.
        :param retain_assets_newer_than: Retain unused assets that were created recently. Default: - all unused assets are removed
        :param schedule: The schedule for the cleaner. Default: - every day
        :param schedule_enabled: Whether to clean on schedule. If you'd like to run the cleanup manually via the console, set to ``false``. Default: true
        '''
        props = ToolkitCleanerProps(
            dry_run=dry_run,
            retain_assets_newer_than=retain_assets_newer_than,
            schedule=schedule,
            schedule_enabled=schedule_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.ToolkitCleanerProps",
    jsii_struct_bases=[],
    name_mapping={
        "dry_run": "dryRun",
        "retain_assets_newer_than": "retainAssetsNewerThan",
        "schedule": "schedule",
        "schedule_enabled": "scheduleEnabled",
    },
)
class ToolkitCleanerProps:
    def __init__(
        self,
        *,
        dry_run: typing.Optional[builtins.bool] = None,
        retain_assets_newer_than: typing.Optional[aws_cdk.Duration] = None,
        schedule: typing.Optional[aws_cdk.aws_events.Schedule] = None,
        schedule_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for a ToolkitCleaner.

        :param dry_run: Only output number of assets and total size that would be deleted but without actually deleting assets.
        :param retain_assets_newer_than: Retain unused assets that were created recently. Default: - all unused assets are removed
        :param schedule: The schedule for the cleaner. Default: - every day
        :param schedule_enabled: Whether to clean on schedule. If you'd like to run the cleanup manually via the console, set to ``false``. Default: true
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if dry_run is not None:
            self._values["dry_run"] = dry_run
        if retain_assets_newer_than is not None:
            self._values["retain_assets_newer_than"] = retain_assets_newer_than
        if schedule is not None:
            self._values["schedule"] = schedule
        if schedule_enabled is not None:
            self._values["schedule_enabled"] = schedule_enabled

    @builtins.property
    def dry_run(self) -> typing.Optional[builtins.bool]:
        '''Only output number of assets and total size that would be deleted but without actually deleting assets.'''
        result = self._values.get("dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retain_assets_newer_than(self) -> typing.Optional[aws_cdk.Duration]:
        '''Retain unused assets that were created recently.

        :default: - all unused assets are removed
        '''
        result = self._values.get("retain_assets_newer_than")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def schedule(self) -> typing.Optional[aws_cdk.aws_events.Schedule]:
        '''The schedule for the cleaner.

        :default: - every day
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[aws_cdk.aws_events.Schedule], result)

    @builtins.property
    def schedule_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to clean on schedule.

        If you'd like to run the cleanup manually
        via the console, set to ``false``.

        :default: true
        '''
        result = self._values.get("schedule_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ToolkitCleanerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UrlShortener(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.UrlShortener",
):
    '''URL shortener.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        api_gateway_authorizer: typing.Optional[aws_cdk.aws_apigateway.IAuthorizer] = None,
        api_gateway_endpoint: typing.Optional[aws_cdk.aws_ec2.IInterfaceVpcEndpoint] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors_allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        expiration: typing.Optional[aws_cdk.Duration] = None,
        record_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: The hosted zone for the short URLs domain.
        :param api_gateway_authorizer: Authorizer for API gateway. Default: - do not use an authorizer for the API
        :param api_gateway_endpoint: An interface VPC endpoint for API gateway. Specifying this property will make the API private. Default: - API is public
        :param bucket_name: A name for the bucket saving the redirects. Default: - derived from short link domain name
        :param cors_allow_origins: Allowed origins for CORS. Default: - CORS is not enabled
        :param expiration: Expiration for short urls. Default: cdk.Duration.days(365)
        :param record_name: The record name to use in the hosted zone. Default: - zone root
        '''
        props = UrlShortenerProps(
            hosted_zone=hosted_zone,
            api_gateway_authorizer=api_gateway_authorizer,
            api_gateway_endpoint=api_gateway_endpoint,
            bucket_name=bucket_name,
            cors_allow_origins=cors_allow_origins,
            expiration=expiration,
            record_name=record_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def api(self) -> aws_cdk.aws_apigateway.LambdaRestApi:
        '''The underlying API Gateway REST API.'''
        return typing.cast(aws_cdk.aws_apigateway.LambdaRestApi, jsii.get(self, "api"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> builtins.str:
        '''The endpoint of the URL shortener API.'''
        return typing.cast(builtins.str, jsii.get(self, "apiEndpoint"))


@jsii.data_type(
    jsii_type="cloudstructs.UrlShortenerProps",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "api_gateway_authorizer": "apiGatewayAuthorizer",
        "api_gateway_endpoint": "apiGatewayEndpoint",
        "bucket_name": "bucketName",
        "cors_allow_origins": "corsAllowOrigins",
        "expiration": "expiration",
        "record_name": "recordName",
    },
)
class UrlShortenerProps:
    def __init__(
        self,
        *,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        api_gateway_authorizer: typing.Optional[aws_cdk.aws_apigateway.IAuthorizer] = None,
        api_gateway_endpoint: typing.Optional[aws_cdk.aws_ec2.IInterfaceVpcEndpoint] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors_allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        expiration: typing.Optional[aws_cdk.Duration] = None,
        record_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for a UrlShortener.

        :param hosted_zone: The hosted zone for the short URLs domain.
        :param api_gateway_authorizer: Authorizer for API gateway. Default: - do not use an authorizer for the API
        :param api_gateway_endpoint: An interface VPC endpoint for API gateway. Specifying this property will make the API private. Default: - API is public
        :param bucket_name: A name for the bucket saving the redirects. Default: - derived from short link domain name
        :param cors_allow_origins: Allowed origins for CORS. Default: - CORS is not enabled
        :param expiration: Expiration for short urls. Default: cdk.Duration.days(365)
        :param record_name: The record name to use in the hosted zone. Default: - zone root
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hosted_zone": hosted_zone,
        }
        if api_gateway_authorizer is not None:
            self._values["api_gateway_authorizer"] = api_gateway_authorizer
        if api_gateway_endpoint is not None:
            self._values["api_gateway_endpoint"] = api_gateway_endpoint
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if cors_allow_origins is not None:
            self._values["cors_allow_origins"] = cors_allow_origins
        if expiration is not None:
            self._values["expiration"] = expiration
        if record_name is not None:
            self._values["record_name"] = record_name

    @builtins.property
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''The hosted zone for the short URLs domain.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def api_gateway_authorizer(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigateway.IAuthorizer]:
        '''Authorizer for API gateway.

        :default: - do not use an authorizer for the API
        '''
        result = self._values.get("api_gateway_authorizer")
        return typing.cast(typing.Optional[aws_cdk.aws_apigateway.IAuthorizer], result)

    @builtins.property
    def api_gateway_endpoint(
        self,
    ) -> typing.Optional[aws_cdk.aws_ec2.IInterfaceVpcEndpoint]:
        '''An interface VPC endpoint for API gateway.

        Specifying this property will
        make the API private.

        :default: - API is public

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html
        '''
        result = self._values.get("api_gateway_endpoint")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IInterfaceVpcEndpoint], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''A name for the bucket saving the redirects.

        :default: - derived from short link domain name
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors_allow_origins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Allowed origins for CORS.

        :default: - CORS is not enabled
        '''
        result = self._values.get("cors_allow_origins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def expiration(self) -> typing.Optional[aws_cdk.Duration]:
        '''Expiration for short urls.

        :default: cdk.Duration.days(365)
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def record_name(self) -> typing.Optional[builtins.str]:
        '''The record name to use in the hosted zone.

        :default: - zone root
        '''
        result = self._values.get("record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UrlShortenerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodeCommitMirror",
    "CodeCommitMirrorProps",
    "CodeCommitMirrorSourceRepository",
    "EcsServiceRoller",
    "EcsServiceRollerProps",
    "EmailReceiver",
    "EmailReceiverProps",
    "IStateMachine",
    "RollTrigger",
    "SamlFederatedPrincipal",
    "SamlIdentityProvider",
    "SamlIdentityProviderProps",
    "SlackApp",
    "SlackAppManifest",
    "SlackAppManifestAppHome",
    "SlackAppManifestDefinition",
    "SlackAppManifestEventSubscriptions",
    "SlackAppManifestInteractivity",
    "SlackAppManifestOauthConfig",
    "SlackAppManifestProps",
    "SlackAppManifestSettings",
    "SlackAppManifestShortcut",
    "SlackAppManifestShortcutType",
    "SlackAppManifestSlashCommand",
    "SlackAppManifestWorkflowStep",
    "SlackAppProps",
    "SlackEvents",
    "SlackEventsProps",
    "SlackTextract",
    "SlackTextractProps",
    "SlackkAppManifestBotUser",
    "StateMachineCustomResourceProvider",
    "StateMachineCustomResourceProviderProps",
    "StaticWebsite",
    "StaticWebsiteProps",
    "ToolkitCleaner",
    "ToolkitCleanerProps",
    "UrlShortener",
    "UrlShortenerProps",
]

publication.publish()
