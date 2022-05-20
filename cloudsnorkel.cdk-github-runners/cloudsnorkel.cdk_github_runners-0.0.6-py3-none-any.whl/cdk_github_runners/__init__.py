'''
# GitHub Self-Hosted Runners CDK Constructs

[![NPM](https://img.shields.io/npm/v/@cloudsnorkel/cdk-github-runners?label=npm&logo=npm)](https://www.npmjs.com/package/@cloudsnorkel/cdk-github-runners)
[![PyPI](https://img.shields.io/pypi/v/cloudsnorkel.cdk-github-runners?label=pypi&logo=pypi)](https://pypi.org/project/cloudsnorkel.cdk-github-runners)
[![Maven Central](https://img.shields.io/maven-central/v/com.cloudsndorkel/cdk.github.runners.svg?label=Maven%20Central&logo=java)](https://search.maven.org/search?q=g:%22com.cloudnsorkel%22%20AND%20a:%22cdk.github.runners%22)
[![Go](https://img.shields.io/github/v/tag/CloudSnorkel/cdk-github-runners?color=red&label=go&logo=go)](https://pkg.go.dev/github.com/CloudSnorkel/cdk-github-runners-go/cloudsnorkelcdkgithubrunners)
[![Nuget](https://img.shields.io/nuget/v/CloudSnorkel.Cdk.Github.Runners?color=red&&logo=nuget)](https://www.nuget.org/packages/CloudSnorkel.Cdk.Github.Runners/)
[![Release](https://github.com/CloudSnorkel/cdk-github-runners/actions/workflows/release.yml/badge.svg)](https://github.com/CloudSnorkel/cdk-github-runners/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](https://github.com/CloudSnorkel/cdk-github-runners/blob/main/LICENSE)

Use this CDK construct to create ephemeral [self-hosted GitHub runners](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners) on-demand inside your AWS account.

* Easy to configure GitHub integration
* Customizable runners with decent defaults
* Supports multiple runner configurations controlled by labels
* Everything fully hosted in your account

Self-hosted runners in AWS are useful when:

* You need easy access to internal resources in your actions
* You want to pre-install some software for your actions
* You want to provide some basic AWS API access ([aws-actions/configure-aws-credentials](https://github.com/marketplace/actions/configure-aws-credentials-action-for-github-actions) has more security controls)

## API

See [API.md](API.md) for full interface documentation.

## Providers

A runner provider creates compute resources on-demand and uses [actions/runner](https://github.com/actions/runner) to start a runner.

| Provider  | Time limit               | vCPUs                    | RAM                               | Storage                      | sudo | Docker |
|-----------|--------------------------|--------------------------|-----------------------------------|------------------------------|------|--------|
| CodeBuild | 8 hours (default 1 hour) | 2 (default), 4, 8, or 72 | 3gb (default), 7gb, 15gb or 145gb | 50gb to 824gb (default 64gb) | ✔    | ✔     |
| Fargate   | Unlimited                | 0.25 to 4 (default 1)    | 512mb to 30gb (default 2gb)       | 20gb to 200gb (default 25gb) | ✔    | TBD    |
| Lambda    | 15 minutes               | 1 to 6 (default 2)       | 128mb to 10gb (default 2gb)       | Up to 10gb (default 10gb)    | ❌    | ❌     |

The best provider to use mostly depends on your current infrastructure. When in doubt, CodeBuild is always a good choice. Execution history and logs are easy to view, and it has no restrictive limits unless you need to run for more than 8 hours.

You can also create your own provider by implementing [`IRunnerProvider`](API.md#IRunnerProvider).

## Installation

1. Confirm you're using CDK v2
2. Install the appropriate package

   1. [Python](https://www.npmjs.com/package/@cloudsnorkel/cdk-github-runners)

      ```
      pip install cloudsnorkel.cdk-github-runners
      ```
   2. [TypeScript or JavaScript](https://pypi.org/project/cloudsnorkel.cdk-github-runners)

      ```
      npm i @cloudsnorkel/cdk-github-runners
      ```
   3. [Java](https://search.maven.org/search?q=g:%22com.cloudnsorkel%22%20AND%20a:%22cdk.github.runners%22)

      ```xml
      <dependency>
      <groupId>com.cloudsnorkel</groupId>
      <artifactId>cdk.github.runners</artifactId>
      </dependency>
      ```
   4. [Go](https://pkg.go.dev/github.com/CloudSnorkel/cdk-github-runners-go/cloudsnorkelcdkgithubrunners)

      ```
      go get github.com/CloudSnorkel/cdk-github-runners-go/cloudsnorkelcdkgithubrunners
      ```
   5. [.NET](https://www.nuget.org/packages/CloudSnorkel.Cdk.Github.Runners/)

      ```
      dotnet add package CloudSnorkel.Cdk.Github.Runners
      ```
3. Use [`GitHubRunners`](API.md#CodeBuildRunner) construct in your code (starting with defaults is fine)
4. Deploy your stack
5. Look for the status command output similar to `aws --region us-east-1 lambda invoke --function-name status-XYZ123 status.json`
6. Execute the status command (you may need to specify `--profile` too) and open the resulting `status.json` file
7. [Setup GitHub](SETUP_GITHUB.md) integration as an app or with personal access token
8. Run status command again to confirm `github.auth.status` and `github.webhook.status` are OK
9. Trigger a GitHub action that has a `self-hosted` label with `runs-on: [self-hosted, linux, codebuild]` or similar
10. If the action is not successful, see [troubleshooting](#Troubleshooting)

## Customizing

The default providers configured by [`GitHubRunners`](API.md#CodeBuildRunner) are useful for testing but probably not too much for actual production work. They run in the default VPC or no VPC and have no added IAM permissions. You would usually want to configure the providers yourself.

For example:

```python
import * as cdk from 'aws-cdk-lib';
import { aws_ec2 as ec2, aws_s3 as s3 } from 'aws-cdk-lib';
import { GitHubRunners, CodeBuildRunner } from '@cloudsnorkel/cdk-github-runners';

const app = new cdk.App();
const stack = new cdk.Stack(
  app,
  'github-runners-test',
  {
     env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION,
     },
  },
);

const vpc = ec2.Vpc.fromLookup(stack, 'vpc', { vpcId: 'vpc-1234567' });
const runnerSg = new ec2.SecurityGroup(stack, 'runner security group', { vpc: vpc });
const dbSg = ec2.SecurityGroup.fromSecurityGroupId(stack, 'database security group', 'sg-1234567');
const bucket = new s3.Bucket(stack, 'runner bucket');

// create a custom CodeBuild provider
const myProvider = new CodeBuildRunner(
  stack, 'codebuild runner',
  {
     label: 'my-codebuild',
     vpc: vpc,
     securityGroup: runnerSg,
  },
);
// grant some permissions to the provider
bucket.grantReadWrite(myProvider);
dbSg.connections.allowFrom(runnerSg, ec2.Port.tcp(3306), 'allow runners to connect to MySQL database');

// create the runner infrastructure
new GitHubRunners(
  stack,
  'runners',
  {
    providers: [myProvider],
    defaultProviderLabel: 'my-codebuild',
  }
);

app.synth();
```

## Architecture

![Architecture diagram](architecture.svg)

## Troubleshooting

1. Always start with the status function, make sure no errors are reported, and confirm all status codes are OK
2. Confirm the webhook Lambda was called by visiting the URL in `troubleshooting.webhookHandlerUrl` from `status.json`

   1. If it's not called or logs errors, confirm the webhook settings on the GitHub side
   2. If you see too many errors, make sure you're only sending `workflow_job` events
3. Check execution details of the orchestrator step function by visiting the URL in `troubleshooting.stepFunctionUrl` from `status.json`

   1. Use the details tab to find the specific execution of the provider (Lambda, CodeBuild, Fargate, etc.)
   2. Every step function execution should be successful, even if the runner action inside it failed

## Other Options

1. [philips-labs/terraform-aws-github-runner](https://github.com/philips-labs/terraform-aws-github-runner) if you're using Terraform
2. [actions-runner-controller/actions-runner-controller](https://github.com/actions-runner-controller/actions-runner-controller) if you're using Kubernetes
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
import aws_cdk.aws_codebuild
import aws_cdk.aws_ec2
import aws_cdk.aws_ecs
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_logs
import aws_cdk.aws_secretsmanager
import aws_cdk.aws_stepfunctions
import constructs


class GitHubRunners(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudsnorkel/cdk-github-runners.GitHubRunners",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        default_provider_label: typing.Optional[builtins.str] = None,
        providers: typing.Optional[typing.Sequence["IRunnerProvider"]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param default_provider_label: 
        :param providers: 

        :stability: experimental
        '''
        props = GitHubRunnersProps(
            default_provider_label=default_provider_label, providers=providers
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="defaultProvider")
    def default_provider(self) -> "IRunnerProvider":
        '''
        :stability: experimental
        '''
        return typing.cast("IRunnerProvider", jsii.get(self, "defaultProvider"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "GitHubRunnersProps":
        '''
        :stability: experimental
        '''
        return typing.cast("GitHubRunnersProps", jsii.get(self, "props"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="providers")
    def providers(self) -> typing.List["IRunnerProvider"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["IRunnerProvider"], jsii.get(self, "providers"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secrets")
    def secrets(self) -> "Secrets":
        '''
        :stability: experimental
        '''
        return typing.cast("Secrets", jsii.get(self, "secrets"))


@jsii.data_type(
    jsii_type="@cloudsnorkel/cdk-github-runners.GitHubRunnersProps",
    jsii_struct_bases=[],
    name_mapping={
        "default_provider_label": "defaultProviderLabel",
        "providers": "providers",
    },
)
class GitHubRunnersProps:
    def __init__(
        self,
        *,
        default_provider_label: typing.Optional[builtins.str] = None,
        providers: typing.Optional[typing.Sequence["IRunnerProvider"]] = None,
    ) -> None:
        '''(experimental) Properties of the GitHubRunners.

        :param default_provider_label: 
        :param providers: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if default_provider_label is not None:
            self._values["default_provider_label"] = default_provider_label
        if providers is not None:
            self._values["providers"] = providers

    @builtins.property
    def default_provider_label(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("default_provider_label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def providers(self) -> typing.Optional[typing.List["IRunnerProvider"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("providers")
        return typing.cast(typing.Optional[typing.List["IRunnerProvider"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubRunnersProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cloudsnorkel/cdk-github-runners.IRunnerProvider")
class IRunnerProvider(
    aws_cdk.aws_ec2.IConnectable,
    aws_cdk.aws_iam.IGrantable,
    typing_extensions.Protocol,
):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''(experimental) GitHub Actions label associated with this runner provider.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security group associated with runners.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC network in which runners will be placed.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="getStepFunctionTask")
    def get_step_function_task(
        self,
        *,
        github_domain_path: builtins.str,
        owner_path: builtins.str,
        repo_path: builtins.str,
        runner_name_path: builtins.str,
        runner_token_path: builtins.str,
    ) -> aws_cdk.aws_stepfunctions.IChainable:
        '''(experimental) Generate step function tasks that execute the runner.

        :param github_domain_path: 
        :param owner_path: 
        :param repo_path: 
        :param runner_name_path: 
        :param runner_token_path: 

        :stability: experimental
        '''
        ...


class _IRunnerProviderProxy(
    jsii.proxy_for(aws_cdk.aws_ec2.IConnectable), # type: ignore[misc]
    jsii.proxy_for(aws_cdk.aws_iam.IGrantable), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cloudsnorkel/cdk-github-runners.IRunnerProvider"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''(experimental) GitHub Actions label associated with this runner provider.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security group associated with runners.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC network in which runners will be placed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))

    @jsii.member(jsii_name="getStepFunctionTask")
    def get_step_function_task(
        self,
        *,
        github_domain_path: builtins.str,
        owner_path: builtins.str,
        repo_path: builtins.str,
        runner_name_path: builtins.str,
        runner_token_path: builtins.str,
    ) -> aws_cdk.aws_stepfunctions.IChainable:
        '''(experimental) Generate step function tasks that execute the runner.

        :param github_domain_path: 
        :param owner_path: 
        :param repo_path: 
        :param runner_name_path: 
        :param runner_token_path: 

        :stability: experimental
        '''
        parameters = RunnerRuntimeParameters(
            github_domain_path=github_domain_path,
            owner_path=owner_path,
            repo_path=repo_path,
            runner_name_path=runner_name_path,
            runner_token_path=runner_token_path,
        )

        return typing.cast(aws_cdk.aws_stepfunctions.IChainable, jsii.invoke(self, "getStepFunctionTask", [parameters]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRunnerProvider).__jsii_proxy_class__ = lambda : _IRunnerProviderProxy


@jsii.implements(IRunnerProvider)
class LambdaRunner(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudsnorkel/cdk-github-runners.LambdaRunner",
):
    '''(experimental) GitHub Actions runner provider using Lambda to execute the actions.

    Creates a Docker-based function that gets executed for each job.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        ephemeral_storage_size: typing.Optional[aws_cdk.Size] = None,
        label: typing.Optional[builtins.str] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional["RunnerVersion"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param ephemeral_storage_size: (experimental) The size of the function’s /tmp directory in MiB. Default: 10 GiB
        :param label: (experimental) GitHub Actions label used for this provider. Default: 'lambda'
        :param memory_size: (experimental) The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 2048
        :param security_group: (experimental) Security Group to assign to this instance. Default: public lambda with no security group
        :param subnet_selection: (experimental) Where to place the network interfaces within the VPC. Default: no subnet
        :param timeout: (experimental) The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.minutes(15)
        :param vpc: (experimental) VPC to launch the runners in. Default: no VPC
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available

        :stability: experimental
        '''
        props = LambdaRunnerProps(
            ephemeral_storage_size=ephemeral_storage_size,
            label=label,
            memory_size=memory_size,
            security_group=security_group,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
            log_retention=log_retention,
            runner_version=runner_version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getStepFunctionTask")
    def get_step_function_task(
        self,
        *,
        github_domain_path: builtins.str,
        owner_path: builtins.str,
        repo_path: builtins.str,
        runner_name_path: builtins.str,
        runner_token_path: builtins.str,
    ) -> aws_cdk.aws_stepfunctions.IChainable:
        '''(experimental) Generate step function tasks that execute the runner.

        :param github_domain_path: 
        :param owner_path: 
        :param repo_path: 
        :param runner_name_path: 
        :param runner_token_path: 

        :stability: experimental
        '''
        parameters = RunnerRuntimeParameters(
            github_domain_path=github_domain_path,
            owner_path=owner_path,
            repo_path=repo_path,
            runner_name_path=runner_name_path,
            runner_token_path=runner_token_path,
        )

        return typing.cast(aws_cdk.aws_stepfunctions.IChainable, jsii.invoke(self, "getStepFunctionTask", [parameters]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> aws_cdk.aws_lambda.Function:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "function"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''(experimental) GitHub Actions label associated with this runner provider.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security group associated with runners.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC network in which runners will be placed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cloudsnorkel/cdk-github-runners.RunnerProviderProps",
    jsii_struct_bases=[],
    name_mapping={"log_retention": "logRetention", "runner_version": "runnerVersion"},
)
class RunnerProviderProps:
    def __init__(
        self,
        *,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional["RunnerVersion"] = None,
    ) -> None:
        '''
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if runner_version is not None:
            self._values["runner_version"] = runner_version

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.ONE_MONTH

        :stability: experimental
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def runner_version(self) -> typing.Optional["RunnerVersion"]:
        '''(experimental) Version of GitHub Runners to install.

        :default: latest version available

        :stability: experimental
        '''
        result = self._values.get("runner_version")
        return typing.cast(typing.Optional["RunnerVersion"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RunnerProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudsnorkel/cdk-github-runners.RunnerRuntimeParameters",
    jsii_struct_bases=[],
    name_mapping={
        "github_domain_path": "githubDomainPath",
        "owner_path": "ownerPath",
        "repo_path": "repoPath",
        "runner_name_path": "runnerNamePath",
        "runner_token_path": "runnerTokenPath",
    },
)
class RunnerRuntimeParameters:
    def __init__(
        self,
        *,
        github_domain_path: builtins.str,
        owner_path: builtins.str,
        repo_path: builtins.str,
        runner_name_path: builtins.str,
        runner_token_path: builtins.str,
    ) -> None:
        '''
        :param github_domain_path: 
        :param owner_path: 
        :param repo_path: 
        :param runner_name_path: 
        :param runner_token_path: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "github_domain_path": github_domain_path,
            "owner_path": owner_path,
            "repo_path": repo_path,
            "runner_name_path": runner_name_path,
            "runner_token_path": runner_token_path,
        }

    @builtins.property
    def github_domain_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("github_domain_path")
        assert result is not None, "Required property 'github_domain_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def owner_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("owner_path")
        assert result is not None, "Required property 'owner_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def repo_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("repo_path")
        assert result is not None, "Required property 'repo_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runner_name_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("runner_name_path")
        assert result is not None, "Required property 'runner_name_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def runner_token_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("runner_token_path")
        assert result is not None, "Required property 'runner_token_path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RunnerRuntimeParameters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RunnerVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudsnorkel/cdk-github-runners.RunnerVersion",
):
    '''
    :stability: experimental
    '''

    def __init__(self, version: builtins.str) -> None:
        '''
        :param version: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [version])

    @jsii.member(jsii_name="latest") # type: ignore[misc]
    @builtins.classmethod
    def latest(cls) -> "RunnerVersion":
        '''
        :stability: experimental
        '''
        return typing.cast("RunnerVersion", jsii.sinvoke(cls, "latest", []))

    @jsii.member(jsii_name="specific") # type: ignore[misc]
    @builtins.classmethod
    def specific(cls, version: builtins.str) -> "RunnerVersion":
        '''
        :param version: -

        :stability: experimental
        '''
        return typing.cast("RunnerVersion", jsii.sinvoke(cls, "specific", [version]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "version"))


class Secrets(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudsnorkel/cdk-github-runners.Secrets",
):
    '''(experimental) Secrets required for GitHub runners operation.

    :stability: experimental
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="github")
    def github(self) -> aws_cdk.aws_secretsmanager.Secret:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.Secret, jsii.get(self, "github"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="githubPrivateKey")
    def github_private_key(self) -> aws_cdk.aws_secretsmanager.Secret:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.Secret, jsii.get(self, "githubPrivateKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="webhook")
    def webhook(self) -> aws_cdk.aws_secretsmanager.Secret:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_secretsmanager.Secret, jsii.get(self, "webhook"))


@jsii.implements(IRunnerProvider)
class CodeBuildRunner(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudsnorkel/cdk-github-runners.CodeBuildRunner",
):
    '''(experimental) GitHub Actions runner provider using CodeBuild to execute the actions.

    Creates a project that gets started for each job.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        compute_type: typing.Optional[aws_cdk.aws_codebuild.ComputeType] = None,
        label: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional[RunnerVersion] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param compute_type: (experimental) The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: {@link ComputeType#SMALL}
        :param label: (experimental) GitHub Actions label used for this provider. Default: 'codebuild'
        :param security_group: (experimental) Security Group to assign to this instance. Default: public project with no security group
        :param subnet_selection: (experimental) Where to place the network interfaces within the VPC. Default: no subnet
        :param timeout: (experimental) The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: (experimental) VPC to launch the runners in. Default: no VPC
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available

        :stability: experimental
        '''
        props = CodeBuildRunnerProps(
            compute_type=compute_type,
            label=label,
            security_group=security_group,
            subnet_selection=subnet_selection,
            timeout=timeout,
            vpc=vpc,
            log_retention=log_retention,
            runner_version=runner_version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getStepFunctionTask")
    def get_step_function_task(
        self,
        *,
        github_domain_path: builtins.str,
        owner_path: builtins.str,
        repo_path: builtins.str,
        runner_name_path: builtins.str,
        runner_token_path: builtins.str,
    ) -> aws_cdk.aws_stepfunctions.IChainable:
        '''(experimental) Generate step function tasks that execute the runner.

        :param github_domain_path: 
        :param owner_path: 
        :param repo_path: 
        :param runner_name_path: 
        :param runner_token_path: 

        :stability: experimental
        '''
        parameters = RunnerRuntimeParameters(
            github_domain_path=github_domain_path,
            owner_path=owner_path,
            repo_path=repo_path,
            runner_name_path=runner_name_path,
            runner_token_path=runner_token_path,
        )

        return typing.cast(aws_cdk.aws_stepfunctions.IChainable, jsii.invoke(self, "getStepFunctionTask", [parameters]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''(experimental) GitHub Actions label associated with this runner provider.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="project")
    def project(self) -> aws_cdk.aws_codebuild.Project:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_codebuild.Project, jsii.get(self, "project"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security group associated with runners.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC network in which runners will be placed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cloudsnorkel/cdk-github-runners.CodeBuildRunnerProps",
    jsii_struct_bases=[RunnerProviderProps],
    name_mapping={
        "log_retention": "logRetention",
        "runner_version": "runnerVersion",
        "compute_type": "computeType",
        "label": "label",
        "security_group": "securityGroup",
        "subnet_selection": "subnetSelection",
        "timeout": "timeout",
        "vpc": "vpc",
    },
)
class CodeBuildRunnerProps(RunnerProviderProps):
    def __init__(
        self,
        *,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional[RunnerVersion] = None,
        compute_type: typing.Optional[aws_cdk.aws_codebuild.ComputeType] = None,
        label: typing.Optional[builtins.str] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available
        :param compute_type: (experimental) The type of compute to use for this build. See the {@link ComputeType} enum for the possible values. Default: {@link ComputeType#SMALL}
        :param label: (experimental) GitHub Actions label used for this provider. Default: 'codebuild'
        :param security_group: (experimental) Security Group to assign to this instance. Default: public project with no security group
        :param subnet_selection: (experimental) Where to place the network interfaces within the VPC. Default: no subnet
        :param timeout: (experimental) The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param vpc: (experimental) VPC to launch the runners in. Default: no VPC

        :stability: experimental
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = aws_cdk.aws_ec2.SubnetSelection(**subnet_selection)
        self._values: typing.Dict[str, typing.Any] = {}
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if runner_version is not None:
            self._values["runner_version"] = runner_version
        if compute_type is not None:
            self._values["compute_type"] = compute_type
        if label is not None:
            self._values["label"] = label
        if security_group is not None:
            self._values["security_group"] = security_group
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if timeout is not None:
            self._values["timeout"] = timeout
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.ONE_MONTH

        :stability: experimental
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def runner_version(self) -> typing.Optional[RunnerVersion]:
        '''(experimental) Version of GitHub Runners to install.

        :default: latest version available

        :stability: experimental
        '''
        result = self._values.get("runner_version")
        return typing.cast(typing.Optional[RunnerVersion], result)

    @builtins.property
    def compute_type(self) -> typing.Optional[aws_cdk.aws_codebuild.ComputeType]:
        '''(experimental) The type of compute to use for this build.

        See the {@link ComputeType} enum for the possible values.

        :default: {@link ComputeType#SMALL}

        :stability: experimental
        '''
        result = self._values.get("compute_type")
        return typing.cast(typing.Optional[aws_cdk.aws_codebuild.ComputeType], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub Actions label used for this provider.

        :default: 'codebuild'

        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security Group to assign to this instance.

        :default: public project with no security group

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def subnet_selection(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) Where to place the network interfaces within the VPC.

        :default: no subnet

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The number of minutes after which AWS CodeBuild stops the build if it's not complete.

        For valid values, see the timeoutInMinutes field in the AWS
        CodeBuild User Guide.

        :default: Duration.hours(1)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC to launch the runners in.

        :default: no VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeBuildRunnerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IRunnerProvider)
class FargateRunner(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cloudsnorkel/cdk-github-runners.FargateRunner",
):
    '''(experimental) GitHub Actions runner provider using Fargate to execute the actions.

    Creates a task definition with a single container that gets started for each job.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.Cluster] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        label: typing.Optional[builtins.str] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional[RunnerVersion] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param assign_public_ip: (experimental) Assign public IP to the runner task. Default: true
        :param cluster: (experimental) Existing Fargate cluster to use. Default: a new cluster
        :param cpu: (experimental) The number of cpu units used by the task. For tasks using the Fargate launch type, this field is required and you must use one of the following values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) 512 (.5 vCPU) - Available memory values: 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) 1024 (1 vCPU) - Available memory values: 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) 2048 (2 vCPU) - Available memory values: Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) 4096 (4 vCPU) - Available memory values: Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) Default: 1024
        :param ephemeral_storage_gib: (experimental) The amount (in GiB) of ephemeral storage to be allocated to the task. The maximum supported value is 200 GiB. NOTE: This parameter is only supported for tasks hosted on AWS Fargate using platform version 1.4.0 or later. Default: 20
        :param label: (experimental) GitHub Actions label used for this provider. Default: 'fargate'
        :param memory_limit_mib: (experimental) The amount (in MiB) of memory used by the task. For tasks using the Fargate launch type, this field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Default: 2048
        :param security_group: (experimental) Security Group to assign to the task. Default: a new security group
        :param vpc: (experimental) VPC to launch the runners in. Default: default account VPC
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available

        :stability: experimental
        '''
        props = FargateRunnerProps(
            assign_public_ip=assign_public_ip,
            cluster=cluster,
            cpu=cpu,
            ephemeral_storage_gib=ephemeral_storage_gib,
            label=label,
            memory_limit_mib=memory_limit_mib,
            security_group=security_group,
            vpc=vpc,
            log_retention=log_retention,
            runner_version=runner_version,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getStepFunctionTask")
    def get_step_function_task(
        self,
        *,
        github_domain_path: builtins.str,
        owner_path: builtins.str,
        repo_path: builtins.str,
        runner_name_path: builtins.str,
        runner_token_path: builtins.str,
    ) -> aws_cdk.aws_stepfunctions.IChainable:
        '''(experimental) Generate step function tasks that execute the runner.

        :param github_domain_path: 
        :param owner_path: 
        :param repo_path: 
        :param runner_name_path: 
        :param runner_token_path: 

        :stability: experimental
        '''
        parameters = RunnerRuntimeParameters(
            github_domain_path=github_domain_path,
            owner_path=owner_path,
            repo_path=repo_path,
            runner_name_path=runner_name_path,
            runner_token_path=runner_token_path,
        )

        return typing.cast(aws_cdk.aws_stepfunctions.IChainable, jsii.invoke(self, "getStepFunctionTask", [parameters]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="assignPublicIp")
    def assign_public_ip(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "assignPublicIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_ecs.Cluster:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs.Cluster, jsii.get(self, "cluster"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connections")
    def connections(self) -> aws_cdk.aws_ec2.Connections:
        '''(experimental) The network connections associated with this resource.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ec2.Connections, jsii.get(self, "connections"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> aws_cdk.aws_ecs.ContainerDefinition:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs.ContainerDefinition, jsii.get(self, "container"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> aws_cdk.aws_iam.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_iam.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="label")
    def label(self) -> builtins.str:
        '''(experimental) GitHub Actions label associated with this runner provider.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "label"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="task")
    def task(self) -> aws_cdk.aws_ecs.FargateTaskDefinition:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_ecs.FargateTaskDefinition, jsii.get(self, "task"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security group associated with runners.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], jsii.get(self, "securityGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC network in which runners will be placed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], jsii.get(self, "vpc"))


@jsii.data_type(
    jsii_type="@cloudsnorkel/cdk-github-runners.FargateRunnerProps",
    jsii_struct_bases=[RunnerProviderProps],
    name_mapping={
        "log_retention": "logRetention",
        "runner_version": "runnerVersion",
        "assign_public_ip": "assignPublicIp",
        "cluster": "cluster",
        "cpu": "cpu",
        "ephemeral_storage_gib": "ephemeralStorageGiB",
        "label": "label",
        "memory_limit_mib": "memoryLimitMiB",
        "security_group": "securityGroup",
        "vpc": "vpc",
    },
)
class FargateRunnerProps(RunnerProviderProps):
    def __init__(
        self,
        *,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional[RunnerVersion] = None,
        assign_public_ip: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_ecs.Cluster] = None,
        cpu: typing.Optional[jsii.Number] = None,
        ephemeral_storage_gib: typing.Optional[jsii.Number] = None,
        label: typing.Optional[builtins.str] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available
        :param assign_public_ip: (experimental) Assign public IP to the runner task. Default: true
        :param cluster: (experimental) Existing Fargate cluster to use. Default: a new cluster
        :param cpu: (experimental) The number of cpu units used by the task. For tasks using the Fargate launch type, this field is required and you must use one of the following values, which determines your range of valid values for the memory parameter: 256 (.25 vCPU) - Available memory values: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) 512 (.5 vCPU) - Available memory values: 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) 1024 (1 vCPU) - Available memory values: 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) 2048 (2 vCPU) - Available memory values: Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) 4096 (4 vCPU) - Available memory values: Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) Default: 1024
        :param ephemeral_storage_gib: (experimental) The amount (in GiB) of ephemeral storage to be allocated to the task. The maximum supported value is 200 GiB. NOTE: This parameter is only supported for tasks hosted on AWS Fargate using platform version 1.4.0 or later. Default: 20
        :param label: (experimental) GitHub Actions label used for this provider. Default: 'fargate'
        :param memory_limit_mib: (experimental) The amount (in MiB) of memory used by the task. For tasks using the Fargate launch type, this field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU) 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU) 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU) Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU) Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU) Default: 2048
        :param security_group: (experimental) Security Group to assign to the task. Default: a new security group
        :param vpc: (experimental) VPC to launch the runners in. Default: default account VPC

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if runner_version is not None:
            self._values["runner_version"] = runner_version
        if assign_public_ip is not None:
            self._values["assign_public_ip"] = assign_public_ip
        if cluster is not None:
            self._values["cluster"] = cluster
        if cpu is not None:
            self._values["cpu"] = cpu
        if ephemeral_storage_gib is not None:
            self._values["ephemeral_storage_gib"] = ephemeral_storage_gib
        if label is not None:
            self._values["label"] = label
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if security_group is not None:
            self._values["security_group"] = security_group
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.ONE_MONTH

        :stability: experimental
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def runner_version(self) -> typing.Optional[RunnerVersion]:
        '''(experimental) Version of GitHub Runners to install.

        :default: latest version available

        :stability: experimental
        '''
        result = self._values.get("runner_version")
        return typing.cast(typing.Optional[RunnerVersion], result)

    @builtins.property
    def assign_public_ip(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Assign public IP to the runner task.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("assign_public_ip")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_ecs.Cluster]:
        '''(experimental) Existing Fargate cluster to use.

        :default: a new cluster

        :stability: experimental
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_ecs.Cluster], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The number of cpu units used by the task.

        For tasks using the Fargate launch type,
        this field is required and you must use one of the following values,
        which determines your range of valid values for the memory parameter:

        256 (.25 vCPU) - Available memory values: 512 (0.5 GB), 1024 (1 GB), 2048 (2 GB)

        512 (.5 vCPU) - Available memory values: 1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB)

        1024 (1 vCPU) - Available memory values: 2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB)

        2048 (2 vCPU) - Available memory values: Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB)

        4096 (4 vCPU) - Available memory values: Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB)

        :default: 1024

        :stability: experimental
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ephemeral_storage_gib(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The amount (in GiB) of ephemeral storage to be allocated to the task.

        The maximum supported value is 200 GiB.

        NOTE: This parameter is only supported for tasks hosted on AWS Fargate using platform version 1.4.0 or later.

        :default: 20

        :stability: experimental
        '''
        result = self._values.get("ephemeral_storage_gib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub Actions label used for this provider.

        :default: 'fargate'

        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The amount (in MiB) of memory used by the task.

        For tasks using the Fargate launch type,
        this field is required and you must use one of the following values, which determines your range of valid values for the cpu parameter:

        512 (0.5 GB), 1024 (1 GB), 2048 (2 GB) - Available cpu values: 256 (.25 vCPU)

        1024 (1 GB), 2048 (2 GB), 3072 (3 GB), 4096 (4 GB) - Available cpu values: 512 (.5 vCPU)

        2048 (2 GB), 3072 (3 GB), 4096 (4 GB), 5120 (5 GB), 6144 (6 GB), 7168 (7 GB), 8192 (8 GB) - Available cpu values: 1024 (1 vCPU)

        Between 4096 (4 GB) and 16384 (16 GB) in increments of 1024 (1 GB) - Available cpu values: 2048 (2 vCPU)

        Between 8192 (8 GB) and 30720 (30 GB) in increments of 1024 (1 GB) - Available cpu values: 4096 (4 vCPU)

        :default: 2048

        :stability: experimental
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security Group to assign to the task.

        :default: a new security group

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC to launch the runners in.

        :default: default account VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FargateRunnerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cloudsnorkel/cdk-github-runners.LambdaRunnerProps",
    jsii_struct_bases=[RunnerProviderProps],
    name_mapping={
        "log_retention": "logRetention",
        "runner_version": "runnerVersion",
        "ephemeral_storage_size": "ephemeralStorageSize",
        "label": "label",
        "memory_size": "memorySize",
        "security_group": "securityGroup",
        "subnet_selection": "subnetSelection",
        "timeout": "timeout",
        "vpc": "vpc",
    },
)
class LambdaRunnerProps(RunnerProviderProps):
    def __init__(
        self,
        *,
        log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
        runner_version: typing.Optional[RunnerVersion] = None,
        ephemeral_storage_size: typing.Optional[aws_cdk.Size] = None,
        label: typing.Optional[builtins.str] = None,
        memory_size: typing.Optional[jsii.Number] = None,
        security_group: typing.Optional[aws_cdk.aws_ec2.ISecurityGroup] = None,
        subnet_selection: typing.Optional[aws_cdk.aws_ec2.SubnetSelection] = None,
        timeout: typing.Optional[aws_cdk.Duration] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        '''
        :param log_retention: (experimental) The number of days log events are kept in CloudWatch Logs. When updating this property, unsetting it doesn't remove the log retention policy. To remove the retention policy, set the value to ``INFINITE``. Default: logs.RetentionDays.ONE_MONTH
        :param runner_version: (experimental) Version of GitHub Runners to install. Default: latest version available
        :param ephemeral_storage_size: (experimental) The size of the function’s /tmp directory in MiB. Default: 10 GiB
        :param label: (experimental) GitHub Actions label used for this provider. Default: 'lambda'
        :param memory_size: (experimental) The amount of memory, in MB, that is allocated to your Lambda function. Lambda uses this value to proportionally allocate the amount of CPU power. For more information, see Resource Model in the AWS Lambda Developer Guide. Default: 2048
        :param security_group: (experimental) Security Group to assign to this instance. Default: public lambda with no security group
        :param subnet_selection: (experimental) Where to place the network interfaces within the VPC. Default: no subnet
        :param timeout: (experimental) The function execution time (in seconds) after which Lambda terminates the function. Because the execution time affects cost, set this value based on the function's expected execution time. Default: Duration.minutes(15)
        :param vpc: (experimental) VPC to launch the runners in. Default: no VPC

        :stability: experimental
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = aws_cdk.aws_ec2.SubnetSelection(**subnet_selection)
        self._values: typing.Dict[str, typing.Any] = {}
        if log_retention is not None:
            self._values["log_retention"] = log_retention
        if runner_version is not None:
            self._values["runner_version"] = runner_version
        if ephemeral_storage_size is not None:
            self._values["ephemeral_storage_size"] = ephemeral_storage_size
        if label is not None:
            self._values["label"] = label
        if memory_size is not None:
            self._values["memory_size"] = memory_size
        if security_group is not None:
            self._values["security_group"] = security_group
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if timeout is not None:
            self._values["timeout"] = timeout
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        '''(experimental) The number of days log events are kept in CloudWatch Logs.

        When updating
        this property, unsetting it doesn't remove the log retention policy. To
        remove the retention policy, set the value to ``INFINITE``.

        :default: logs.RetentionDays.ONE_MONTH

        :stability: experimental
        '''
        result = self._values.get("log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    @builtins.property
    def runner_version(self) -> typing.Optional[RunnerVersion]:
        '''(experimental) Version of GitHub Runners to install.

        :default: latest version available

        :stability: experimental
        '''
        result = self._values.get("runner_version")
        return typing.cast(typing.Optional[RunnerVersion], result)

    @builtins.property
    def ephemeral_storage_size(self) -> typing.Optional[aws_cdk.Size]:
        '''(experimental) The size of the function’s /tmp directory in MiB.

        :default: 10 GiB

        :stability: experimental
        '''
        result = self._values.get("ephemeral_storage_size")
        return typing.cast(typing.Optional[aws_cdk.Size], result)

    @builtins.property
    def label(self) -> typing.Optional[builtins.str]:
        '''(experimental) GitHub Actions label used for this provider.

        :default: 'lambda'

        :stability: experimental
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def memory_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The amount of memory, in MB, that is allocated to your Lambda function.

        Lambda uses this value to proportionally allocate the amount of CPU
        power. For more information, see Resource Model in the AWS Lambda
        Developer Guide.

        :default: 2048

        :stability: experimental
        '''
        result = self._values.get("memory_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def security_group(self) -> typing.Optional[aws_cdk.aws_ec2.ISecurityGroup]:
        '''(experimental) Security Group to assign to this instance.

        :default: public lambda with no security group

        :stability: experimental
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.ISecurityGroup], result)

    @builtins.property
    def subnet_selection(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetSelection]:
        '''(experimental) Where to place the network interfaces within the VPC.

        :default: no subnet

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SubnetSelection], result)

    @builtins.property
    def timeout(self) -> typing.Optional[aws_cdk.Duration]:
        '''(experimental) The function execution time (in seconds) after which Lambda terminates the function.

        Because the execution time affects cost, set this value
        based on the function's expected execution time.

        :default: Duration.minutes(15)

        :stability: experimental
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[aws_cdk.Duration], result)

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        '''(experimental) VPC to launch the runners in.

        :default: no VPC

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaRunnerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodeBuildRunner",
    "CodeBuildRunnerProps",
    "FargateRunner",
    "FargateRunnerProps",
    "GitHubRunners",
    "GitHubRunnersProps",
    "IRunnerProvider",
    "LambdaRunner",
    "LambdaRunnerProps",
    "RunnerProviderProps",
    "RunnerRuntimeParameters",
    "RunnerVersion",
    "Secrets",
]

publication.publish()
