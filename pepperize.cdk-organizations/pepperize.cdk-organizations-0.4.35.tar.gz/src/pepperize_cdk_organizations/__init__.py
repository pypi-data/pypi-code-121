'''
[![GitHub](https://img.shields.io/github/license/pepperize/cdk-organizations?style=flat-square)](https://github.com/pepperize/cdk-organizations/blob/main/LICENSE)
[![npm (scoped)](https://img.shields.io/npm/v/@pepperize/cdk-organizations?style=flat-square)](https://www.npmjs.com/package/@pepperize/cdk-organizations)
[![PyPI](https://img.shields.io/pypi/v/pepperize.cdk-organizations?style=flat-square)](https://pypi.org/project/pepperize.cdk-organizations/)
[![Nuget](https://img.shields.io/nuget/v/Pepperize.CDK.Organizations?style=flat-square)](https://www.nuget.org/packages/Pepperize.CDK.Organizations/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/pepperize/cdk-organizations/release/main?label=release&style=flat-square)](https://github.com/pepperize/cdk-organizations/actions/workflows/release.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/pepperize/cdk-organizations?sort=semver&style=flat-square)](https://github.com/pepperize/cdk-organizations/releases)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod&style=flat-square)](https://gitpod.io/#https://github.com/pepperize/cdk-organizations)

# CDK Organizations

Manage AWS organizations, organizational units (OU), accounts and service control policies (SCP).

Motivation:

> Currently, there is no `aws-cdk-lib/organizations` available. See this [Issue on AWS CDK](https://github.com/aws/aws-cdk/issues/2877).

## References

* [CDK Organizations API Reference](https://github.com/pepperize/cdk-organizations/blob/main/API.md)
* [AWS Account Management Reference Guide](https://docs.aws.amazon.com/accounts/latest/reference/accounts-welcome.html)
* [AWS Organizations User Guide](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
* [AWS API Reference](https://docs.aws.amazon.com/organizations/latest/APIReference/Welcome.html)
* [AWS CDK Custom Resources](https://docs.aws.amazon.com/cdk/api/v1/docs/custom-resources-readme.html#custom-resources-for-aws-apis)

## Install

### TypeScript

```shell
npm install @pepperize/cdk-organizations
```

or

```shell
yarn add @pepperize/cdk-organizations
```

### Python

```shell
pip install pepperize.cdk-organizations
```

### C# / .Net

```
dotnet add package Pepperize.CDK.Organizations
```

## Getting Started

1. Create a new account

   [Signup for AWS](https://portal.aws.amazon.com/billing/signup#/start)
2. Prepare an IAM User with `AdministratorAccess`

   To deploy your new organization, you have to create an Administrator with an AccessKey

   * [Creating your first IAM admin user and user group](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html)
   * [Managing access keys for IAM users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey)
3. Create a new CDK TypeScript App project with [projen](https://github.com/projen/projen)

   ```shell
   mkdir my-project
   cd my-project
   git init -b main
   npx projen new awscdk-app-ts
   ```
4. Add `@pepperize/cdk-organizations` to your dependencies in `.projenrc.js`

   ```python
   const project = new awscdk.AwsCdkTypeScriptApp({
     //...
     deps: ["@pepperize/cdk-organizations"],
   });
   ```
5. Install the dependency

   ```shell
   npx projen
   ```
6. Create a stack

   ```python
   import { Account, Organization, OrganizationalUnit } from "@pepperize/cdk-organizations";
   import { Stack } from "aws-cdk-lib";

   export class OrganizationStack extends Stack {
     constructor(scope: Construct, id: string, props: StackProps = {}) {
       super(scope, id, { ...props, env: { ...props.env, region: "us-east-1" } }); // AWS Organizations API is only available in region us-east-1

       // Create your organization
       const organization = new Organization(stack, "Organization", {});

       // Create an organizational unit (OU)
       const organizationUnit = new OrganizationalUnit(stack, "OrganizationalUnit", {
         organizationalUnitName: "MyFirstOU",
         parent: organization.root,
       });

       // Create an account
       const account = new Account(stack, "Account", {
         accountName: "MyFirstAccount",
         email: "<your email for the member account>",
         parent: organizationUnit,
       });
     }
   }
   ```
7. Configure your AWS CLI to deploy

   * [Configuring the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
   * [AWSume](https://awsu.me/)

   The easiest is to export your access key

   ```shell
   export AWS_ACCESS_KEY_ID=<your created access key id>
   export AWS_SECRET_ACCESS_KEY=<your created secret access key>
   ```
8. Deploy your first AWS organization

   ```shell
   export CDK_DEFAULT_REGION=us-east-1
   export CDK_DEFAULT_ACCOUNT=<your AWS account id>
   ```

   ```shell
   yarn deploy
   ```

## Usage

### Organization

To create a new organization or import an existing organization, add the following construct to your stack:

```python
const organization = new Organization(stack, "Organization", {
  featureSet: FeatureSet.ALL, // (default) required later on to enable SCPs, enable AWS services or delegate an adminsitrator account
});
organization.root; // The organization's root is automatically created
```

* `FeatureSet.ALL` is required for advanced features like Service Control Policies (SCP) and is the [preferred way to work with AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html)
* The account which deploys the stack, will automatically become the management account of the new organization.
* If an organization already exists, it will be imported automatically. You can disable this behaviour by passing `importOnDuplicate: false` in the props.
* If the construct is removed from the stack, the organization will remain and must be deleted manually. For deletion of an organization you must previously remove all the member accounts, OUs, and policies from the organization. [Deleting the organization by removing the management account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_delete.html)
* An organization root is automatically created for you when you create the new organization.

See [IOrganization](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.IOrganization)

### Organizational Unit (OU)

To create a new organizational unit (OU), add the following construct to your stack:

```python
const organizationUnit = new OrganizationalUnit(stack, "Organization", {
  organizationalUnitName: "Project2",
  parent: organization.root,
});
```

* The parent of an organizational unit (OU) can be either the organization's root or another OU within the organization.
* An organizational unit (OU) can't be moved. You have to create a new OU first, move all the accounts and then delete the old OU.
* For deletion of an organizational unit (OU) you must first move all accounts out of the OU and any child OUs, and then you can delete the child OUs. [Deleting an organizational unit](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html#delete-ou)

See [IOrganizationalUnit](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.IOrganizationalUnit)

#### Organizational Unit (OU) Properties

* `importOnDuplicate` If an organizational unit (OU) with the name exists in the parent, it will be imported.
* `removalPolicy` Default `RemovalPolicy.Retain` If you set `removalPolicy` to `RemovalPolicy.destroy`, the organizational unit (OU) will be deleted on Cloudformation delete event.

See [OrganizationalUnitProps](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.OrganizationalUnitProps)

### Account

To create a new account, add the following construct to your stack:

```python
new Account(stack, "Account", {
  accountName: "MyAccount",
  email: "info@pepperize.com",
  parent: organization.root,
});
```

* The email address must not already be associated with another AWS account. You may suffix the email address, i.e. `info+account-123456789012@pepperize.com`.
* An account will be created and moved to the parent, if the parent is an organizational unit (OU).
* An account can only be created from within the management account in the `us-east-1` region.

See [IAccount](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.IAccount)

#### Account Properties

* `importOnDuplicate` If an account with the same email address exists in the organization, it will be imported.
* `removalPolicy` Default `RemovalPolicy.Retain` If you set `removalPolicy` to `RemovalPolicy.destroy`, the account will be closed. [Closing an AWS account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_close.html)
* `iamUserAccessToBilling` Default `IamUserAccessToBilling.ALLOW` If you set `iamUserAccessToBilling` to `ALLOW`, IAM users and roles that have appropriate permissions can view billing information for the account.
* `roleName` Default `OrganizationAccountAccessRole` is preconfigures in the newly created account and grants users in the management account administrator permissions in the new member account.

See [AccountProps](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.AccountProps)

### Delegated Administrator

A compatible AWS service (trusted service) can register an AWS member account in the organization as an administrator in the organization on your behalf. To enable an AWS account as administrator of that trusted in your organization call `delegateAdministrator` on your account:

```python
const account = new Account(stack, "Account", {
  accountName: "StackSetsDelegatedAdministrator",
  email: "info@pepperize.com",
});
account.delegateAdministrator("stacksets.amazonaws.com");
```

* [AWS services that support Delegated Administrator](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html)
* To be able to use Delegated Administrator, your organization must have [all features](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.FeatureSet) enabled.

See [DelegatedAdministrator](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.DelegatedAdministrator)

### Enable an AWS Service (trusted service)

To enable trusted access for a supported AWS service (trusted service), which performs tasks in your organization and its accounts on your behalf, call `enableAwsService` on your organization:

```python
const organization = new Organization(stack, "Organization", {
  featureSet: FeatureSet.ALL, // (default) the organization must be created with all features enabled
});
organization.enableAwsServiceAccess("ssm.amazonaws.com");
```

* To enable trusted access, you must have [all features](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.FeatureSet) enabled.
* It's recommended to use only the trusted service's console [How to enable or disable trusted access](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html#orgs_how-to-enable-disable-trusted-access)
* [AWS services that you can use with AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html)

See [EnableAwsServiceAccess](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.EnableAwsServiceAccess)

### Enable a Policy Type

To enable a policy type call `enablePolicyType` on your organization.

```python
const organization = new Organization(stack, "Organization", {
  featureSet: FeatureSet.ALL, // (default) the organization must be created with all features enabled
});
organization.enablePolicyType(PolicyType.SERVICE_CONTROL_POLICY);
organization.enablePolicyType(PolicyType.TAG_POLICY);
organization.enablePolicyType(PolicyType.BACKUP_POLICY);
organization.enablePolicyType(PolicyType.AISERVICES_OPT_OUT_POLICY);
```

* To create or attach policies later on, you have to [enable all features](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.FeatureSet) and the [policy type](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types) .

See [EnablePolicyType](https://github.com/pepperize/cdk-organizations/blob/main/API.md#enablepolicytype-), [PolicyType](https://github.com/pepperize/cdk-organizations/blob/main/API.md#policytype-).

### Policy

To create a new policy add the following construct to your stack:

```python
new Policy(stack, "Policy", {
  content: '{\n"Version":"2012-10-17","Statement":{\n"Effect":"Allow","Action":"s3:*"\n}\n}',
  description: "Enables admins of attached accounts to delegate all S3 permissions",
  policyName: "AllowAllS3Actions",
  policyType: PolicyType.SERVICE_CONTROL_POLICY,
});
```

* To create or attach policies, you must have [all features](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.FeatureSet) and the [policy type](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types) enabled.
* The [SCP Syntax](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_syntax.html) is quite similar to IAM policies, but way more limited.

See [Policy](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.Policy)

### Attach a policy

To attach a policy to a root, an organizational unit (OU), or an individual account call `attachPolicy` with the policy to attach:

```python
organization.enablePolicyType(PolicyType.TAG_POLICY);

const policy = new Policy(stack, "Policy", {
  content: '{\n"tags":{\n"CostCenter":{\n"tag_key":{\n"@@assign":"CostCenter"\n}\n}\n}\n}',
  description: "Defines the CostCenter tag key",
  policyName: "CostCenterTag",
  policyType: PolicyType.TAG_POLICY,
});

organization.attachPolicy(policy);
organizationalUnit.attachPolicy(policy);
account.attachPolicy(policy);
```

* To create or attach policies, you must have [all features](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.FeatureSet) and the [policy type](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types) enabled.

### Tagging resources

To tag a resource you may follow the [AWS CDK Developer Guide - Tagging](https://docs.aws.amazon.com/cdk/v2/guide/tagging.html):

You can add one or more tags to the following resources in AWS Organizations.

* Account
* Organization root
* Organizational unit (OU)
* Policy

See [Tagging AWS Organizations resources](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_tagging.html), [ITaggableResource](https://github.com/pepperize/cdk-organizations/blob/main/API.md#@pepperize/cdk-organizations.ITaggableResource)

#### Tagging an organization's root

```python
import { Tags } from "aws-cdk-lib";

const organization = new Organization();
Tags.of(organization.root).add("key", "value");
```

#### Tagging an organizational unit (OU)

```python
import { Tags } from "aws-cdk-lib";

const organizationalUnit = new OrganizationalUnit();
Tags.of(organizationalUnit).add("key", "value");
```

#### Tagging an account

```python
import { Tags } from "aws-cdk-lib";

const account = new Account();
Tags.of(account).add("key", "value");
```

#### Tagging a policy

```python
import { Tags } from "aws-cdk-lib";

const policy = new Policy();
Tags.of(policy).add("key", "value");
```

## Limitations

AWS Organizations has some limitations:

* The stack should be deployed in the `us-east-1` region.
* The stack's account must be the management account of an existing organization.
* The stack's account becomes the management account of the new organization.
* An account belongs to only one organization within a single root.
* [Quotas for AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_reference_limits.html)

# Contributing

Contributions of all kinds are welcome :rocket: Check out our [contributor's guide](https://github.com/pepperize/cdk-organizations/blob/main/CONTRIBUTING.md).

For a quick start, check out a development environment:

```shell
git clone git@github.com:pepperize/cdk-organizations
cd cdk-organizations
# install dependencies
yarn
# build with projen
yarn build
```

# Example

See [example](https://github.com/pepperize/cdk-organizations-example/blob/main/src/example-stack.ts)

```python
import { App, Stack } from "aws-cdk-lib/core";
import {
  Account,
  DelegatedAdministrator,
  EnableAwsServiceAccess,
  EnablePolicyType,
  FeatureSet,
  IamUserAccessToBilling,
  Organization,
  OrganizationalUnit,
  Policy,
  PolicyAttachment,
  PolicyType,
} from "@pepperize/cdk-organizations";

const app = new App();
const stack = new Stack(app);

// Create an organization
const organization = new Organization(stack, "Organization", {
  featureSet: FeatureSet.ALL,
});
// Enable AWS Service Access (requires FeatureSet: ALL)
organization.enableAwsServiceAccess("service-abbreviation.amazonaws.com");

// Create an account
const account = new Account(stack, "SharedAccount", {
  accountName: "SharedAccount",
  email: "info+shared-account@pepperize.com",
  roleName: "OrganizationAccountAccessRole",
  iamUserAccessToBilling: IamUserAccessToBilling.ALLOW,
  parent: organization.root,
});
// Enable a delegated admin account
account.delegateAdministrator("service-abbreviation.amazonaws.com");

// Create an OU in the current organizations root
const projects = new OrganizationalUnit(stack, "ProjectsOU", {
  organizationalUnitName: "Projects",
  parent: organization.root,
});
new Account(stack, "Project1Account", {
  accountName: "SharedAccount",
  email: "info+project1@pepperize.com",
  parent: projects,
});

// Create a nested OU and attach two accounts
const project2 = new OrganizationalUnit(stack, "Project2OU", {
  organizationalUnitName: "Project2",
  parent: projects,
});
new Account(stack, "Project2DevAccount", {
  accountName: "Project 2 Dev",
  email: "info+project2-dev@pepperize.com",
  parent: project2,
});
new Account(stack, "Project2ProdAccount", {
  accountName: "Project 2 Prod",
  email: "info+project2-prod@pepperize.com",
  parent: project2,
});

// Enable the service control policy (SCP) type within the organization
organization.enablePolicyType(PolicyType.SERVICE_CONTROL_POLICY);
// Create and attach and Service Control Policy (SCP)
const policy = new Policy(stack, "Policy", {
  content: '{\n"Version":"2012-10-17","Statement":{\n"Effect":"Allow","Action":"s3:*"\n}\n}',
  description: "Enables admins of attached accounts to delegate all S3 permissions",
  policyName: "AllowAllS3Actions",
  policyType: PolicyType.SERVICE_CONTROL_POLICY,
});
organization.attachPolicy(policy);

// Tagging AWS organization resources of this stack
Tags.of(stack).add("tagKey", "tagValue");
```

# Alternatives

* [AWS Bootstrap Kit](https://github.com/awslabs/aws-bootstrap-kit)
* [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
* [AWS Deployment Framework (ADF)](https://github.com/awslabs/aws-deployment-framework)
* [AWS Organization Formation](https://github.com/org-formation)
* [AWS Control Tower Account Factory for Terraform (ATF)](https://github.com/aws-ia/terraform-aws-control_tower_account_factory)
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
import aws_cdk.custom_resources
import constructs


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.AccountProps",
    jsii_struct_bases=[],
    name_mapping={
        "account_name": "accountName",
        "email": "email",
        "iam_user_access_to_billing": "iamUserAccessToBilling",
        "import_on_duplicate": "importOnDuplicate",
        "parent": "parent",
        "removal_policy": "removalPolicy",
        "role_name": "roleName",
    },
)
class AccountProps:
    def __init__(
        self,
        *,
        account_name: builtins.str,
        email: builtins.str,
        iam_user_access_to_billing: typing.Optional["IamUserAccessToBilling"] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
        parent: typing.Optional["IParent"] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param account_name: (experimental) The friendly name of the member account.
        :param email: (experimental) The email address of the owner to assign to the new member account. This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        :param iam_user_access_to_billing: (experimental) If set to ALLOW , the new account enables IAM users to access account billing information if they have the required permissions. If set to DENY , only the root user of the new account can access account billing information. Default: ALLOW
        :param import_on_duplicate: (experimental) Whether to import, if a duplicate account with same name and email already exists. Default: true
        :param parent: (experimental) The parent root or OU that you want to create the new Account in.
        :param removal_policy: (experimental) If set to RemovalPolicy.DESTROY, the account will be moved to the root. Default: RemovalPolicy.Retain
        :param role_name: (experimental) The name of an IAM role that AWS Organizations automatically preconfigures in the new member account. This role trusts the management account, allowing users in the management account to assume the role, as permitted by the management account administrator. The role has administrator permissions in the new member account. If you don't specify this parameter, the role name defaults to OrganizationAccountAccessRole.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account_name": account_name,
            "email": email,
        }
        if iam_user_access_to_billing is not None:
            self._values["iam_user_access_to_billing"] = iam_user_access_to_billing
        if import_on_duplicate is not None:
            self._values["import_on_duplicate"] = import_on_duplicate
        if parent is not None:
            self._values["parent"] = parent
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if role_name is not None:
            self._values["role_name"] = role_name

    @builtins.property
    def account_name(self) -> builtins.str:
        '''(experimental) The friendly name of the member account.

        :stability: experimental
        '''
        result = self._values.get("account_name")
        assert result is not None, "Required property 'account_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email(self) -> builtins.str:
        '''(experimental) The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.

        :stability: experimental
        '''
        result = self._values.get("email")
        assert result is not None, "Required property 'email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def iam_user_access_to_billing(self) -> typing.Optional["IamUserAccessToBilling"]:
        '''(experimental) If set to ALLOW , the new account enables IAM users to access account billing information if they have the required permissions.

        If set to DENY , only the root user of the new account can access account billing information.

        :default: ALLOW

        :stability: experimental
        '''
        result = self._values.get("iam_user_access_to_billing")
        return typing.cast(typing.Optional["IamUserAccessToBilling"], result)

    @builtins.property
    def import_on_duplicate(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to import, if a duplicate account with same name and email already exists.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("import_on_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def parent(self) -> typing.Optional["IParent"]:
        '''(experimental) The parent root or OU that you want to create the new Account in.

        :stability: experimental
        '''
        result = self._values.get("parent")
        return typing.cast(typing.Optional["IParent"], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) If set to RemovalPolicy.DESTROY, the account will be moved to the root.

        :default: RemovalPolicy.Retain

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    @builtins.property
    def role_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of an IAM role that AWS Organizations automatically preconfigures in the new member account.

        This role trusts the management account, allowing users in the management account to assume the role, as permitted by the management account administrator. The role has administrator permissions in the new member account.

        If you don't specify this parameter, the role name defaults to OrganizationAccountAccessRole.

        :stability: experimental
        '''
        result = self._values.get("role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccountProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DelegatedAdministrator(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.DelegatedAdministrator",
):
    '''(experimental) Enables the specified member account to administer the Organizations features of the specified AWS service.

    It grants read-only access to AWS Organizations service data. The account still requires IAM permissions to access and administer the AWS service.

    You can run this action only for AWS services that support this feature. For a current list of services that support it, see the column Supports Delegated Administrator in the table at AWS Services that you can use with AWS Organizations in the `AWS Organizations User Guide <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html>`_.

    :see: https://docs.aws.amazon.com/accounts/latest/reference/using-orgs-delegated-admin.html
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account: "IAccount",
        service_principal: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: (experimental) The member account in the organization to register as a delegated administrator.
        :param service_principal: (experimental) The service principal of the AWS service for which you want to make the member account a delegated administrator.

        :stability: experimental
        '''
        props = DelegatedAdministratorProps(
            account=account, service_principal=service_principal
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.DelegatedAdministratorProps",
    jsii_struct_bases=[],
    name_mapping={"account": "account", "service_principal": "servicePrincipal"},
)
class DelegatedAdministratorProps:
    def __init__(self, *, account: "IAccount", service_principal: builtins.str) -> None:
        '''
        :param account: (experimental) The member account in the organization to register as a delegated administrator.
        :param service_principal: (experimental) The service principal of the AWS service for which you want to make the member account a delegated administrator.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "account": account,
            "service_principal": service_principal,
        }

    @builtins.property
    def account(self) -> "IAccount":
        '''(experimental) The member account in the organization to register as a delegated administrator.

        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast("IAccount", result)

    @builtins.property
    def service_principal(self) -> builtins.str:
        '''(experimental) The service principal of the AWS service for which you want to make the member account a delegated administrator.

        :stability: experimental
        '''
        result = self._values.get("service_principal")
        assert result is not None, "Required property 'service_principal' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DelegatedAdministratorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnableAwsServiceAccess(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.EnableAwsServiceAccess",
):
    '''(experimental) Enables the integration of an AWS service (the service that is specified by ServicePrincipal) with AWS Organizations.

    When you enable integration, you allow the specified service to create a service-linked role in all the accounts in your organization. This allows the service to perform operations on your behalf in your organization and its accounts.

    This operation can be called only from the organization's management account and only if the organization has enabled all features.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services.html#orgs_trusted_access_perms
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        service_principal: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param service_principal: (experimental) The service principal name of the AWS service for which you want to enable integration with your organization. This is typically in the form of a URL, such as service-abbreviation.amazonaws.com.

        :stability: experimental
        '''
        props = EnableAwsServiceAccessProps(service_principal=service_principal)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.EnableAwsServiceAccessProps",
    jsii_struct_bases=[],
    name_mapping={"service_principal": "servicePrincipal"},
)
class EnableAwsServiceAccessProps:
    def __init__(self, *, service_principal: builtins.str) -> None:
        '''
        :param service_principal: (experimental) The service principal name of the AWS service for which you want to enable integration with your organization. This is typically in the form of a URL, such as service-abbreviation.amazonaws.com.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "service_principal": service_principal,
        }

    @builtins.property
    def service_principal(self) -> builtins.str:
        '''(experimental) The service principal name of the AWS service for which you want to enable integration with your organization.

        This is typically in the form of a URL, such as service-abbreviation.amazonaws.com.

        :stability: experimental
        '''
        result = self._values.get("service_principal")
        assert result is not None, "Required property 'service_principal' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnableAwsServiceAccessProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EnablePolicyType(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.EnablePolicyType",
):
    '''(experimental) Enables and disables Enables a policy type in a root.

    After you enable a policy type in a root, you can attach policies of that type to the root, any organizational unit (OU), or account in that root.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy_type: "PolicyType",
        root: "Root",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param policy_type: 
        :param root: 

        :stability: experimental
        '''
        props = EnablePolicyTypeProps(policy_type=policy_type, root=root)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.EnablePolicyTypeProps",
    jsii_struct_bases=[],
    name_mapping={"policy_type": "policyType", "root": "root"},
)
class EnablePolicyTypeProps:
    def __init__(self, *, policy_type: "PolicyType", root: "Root") -> None:
        '''
        :param policy_type: 
        :param root: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy_type": policy_type,
            "root": root,
        }

    @builtins.property
    def policy_type(self) -> "PolicyType":
        '''
        :stability: experimental
        '''
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast("PolicyType", result)

    @builtins.property
    def root(self) -> "Root":
        '''
        :stability: experimental
        '''
        result = self._values.get("root")
        assert result is not None, "Required property 'root' is missing"
        return typing.cast("Root", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnablePolicyTypeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@pepperize/cdk-organizations.FeatureSet")
class FeatureSet(enum.Enum):
    '''(experimental) Specifies the feature set supported by the new organization.

    Each feature set supports different levels of functionality.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#feature-set
    :stability: experimental
    '''

    CONSOLIDATED_BILLING = "CONSOLIDATED_BILLING"
    '''(experimental) All member accounts have their bills consolidated to and paid by the management account.

    For more information, see `Consolidated billing <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#feature-set-cb-only>`_ in the AWS Organizations User Guide. The consolidated billing feature subset isn’t available for organizations in the AWS GovCloud (US) Region.

    :stability: experimental
    '''
    ALL = "ALL"
    '''(experimental) In addition to all the features supported by the consolidated billing feature set, the management account can also apply any policy type to any member account in the organization.

    For more information, see `All features <https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html#feature-set-all>`_ in the AWS Organizations User Guide.

    :stability: experimental
    '''


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IOrganization")
class IOrganization(constructs.IConstruct, typing_extensions.Protocol):
    '''(experimental) Creates an organization to consolidate your AWS accounts so that you can administer them as a single unit.

    An organization has one management account along with zero or more member accounts. You can organize the accounts in a hierarchical, tree-like structure with a root at the top and organizational units nested under the root. Each account can be directly in the root, or placed in one of the OUs in the hierarchy. An organization has the functionality that is determined by the feature set that you enable.

    The account whose user is calling the CreateOrganization operation automatically becomes the management account of the new organization.

    For deletion of an organization you must previously remove all the member accounts, OUs, and policies from the organization!

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_create.html#create-org
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureSet")
    def feature_set(self) -> FeatureSet:
        '''(experimental) Specifies the functionality that currently is available to the organization.

        If set to "ALL", then all features are enabled and policies can be applied to accounts in the organization. If set to "CONSOLIDATED_BILLING", then only consolidated billing functionality is available.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountArn")
    def management_account_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the account that is designated as the management account for the organization.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountEmail")
    def management_account_email(self) -> builtins.str:
        '''(experimental) The email address that is associated with the AWS account that is designated as the management account for the organization.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountId")
    def management_account_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the management account of an organization.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArn")
    def organization_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of an organization.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of an organization.

        The regex pattern for an organization ID string requires "o-" followed by from 10 to 32 lowercase letters or digits.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "Root":
        '''(experimental) The root of the current organization, which is automatically created.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="enableAwsServiceAccess")
    def enable_aws_service_access(self, service_principal: builtins.str) -> None:
        '''(experimental) Enables trusted access for a supported AWS service (trusted service), which performs tasks in your organization and its accounts on your behalf.

        :param service_principal: The supported AWS service that you specify.

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html
        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="enablePolicyType")
    def enable_policy_type(self, policy_type: "PolicyType") -> None:
        '''(experimental) Enables policy types in the following two broad categories: Authorization policies and Management policies.

        :param policy_type: : the type of the policy that you specify.

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types
        :stability: experimental
        '''
        ...


class _IOrganizationProxy(
    jsii.proxy_for(constructs.IConstruct) # type: ignore[misc]
):
    '''(experimental) Creates an organization to consolidate your AWS accounts so that you can administer them as a single unit.

    An organization has one management account along with zero or more member accounts. You can organize the accounts in a hierarchical, tree-like structure with a root at the top and organizational units nested under the root. Each account can be directly in the root, or placed in one of the OUs in the hierarchy. An organization has the functionality that is determined by the feature set that you enable.

    The account whose user is calling the CreateOrganization operation automatically becomes the management account of the new organization.

    For deletion of an organization you must previously remove all the member accounts, OUs, and policies from the organization!

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_create.html#create-org
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IOrganization"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureSet")
    def feature_set(self) -> FeatureSet:
        '''(experimental) Specifies the functionality that currently is available to the organization.

        If set to "ALL", then all features are enabled and policies can be applied to accounts in the organization. If set to "CONSOLIDATED_BILLING", then only consolidated billing functionality is available.

        :stability: experimental
        '''
        return typing.cast(FeatureSet, jsii.get(self, "featureSet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountArn")
    def management_account_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the account that is designated as the management account for the organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "managementAccountArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountEmail")
    def management_account_email(self) -> builtins.str:
        '''(experimental) The email address that is associated with the AWS account that is designated as the management account for the organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "managementAccountEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountId")
    def management_account_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the management account of an organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "managementAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArn")
    def organization_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of an organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of an organization.

        The regex pattern for an organization ID string requires "o-" followed by from 10 to 32 lowercase letters or digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "Root":
        '''(experimental) The root of the current organization, which is automatically created.

        :stability: experimental
        '''
        return typing.cast("Root", jsii.get(self, "root"))

    @jsii.member(jsii_name="enableAwsServiceAccess")
    def enable_aws_service_access(self, service_principal: builtins.str) -> None:
        '''(experimental) Enables trusted access for a supported AWS service (trusted service), which performs tasks in your organization and its accounts on your behalf.

        :param service_principal: The supported AWS service that you specify.

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "enableAwsServiceAccess", [service_principal]))

    @jsii.member(jsii_name="enablePolicyType")
    def enable_policy_type(self, policy_type: "PolicyType") -> None:
        '''(experimental) Enables policy types in the following two broad categories: Authorization policies and Management policies.

        :param policy_type: : the type of the policy that you specify.

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "enablePolicyType", [policy_type]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOrganization).__jsii_proxy_class__ = lambda : _IOrganizationProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IPolicy")
class IPolicy(constructs.IConstruct, typing_extensions.Protocol):
    '''(experimental) Policies in AWS Organizations enable you to apply additional types of management to the AWS accounts in your organization.

    You can use policies when all features are enabled in your organization.

    Before you can create and attach a policy to your organization, you must enable that policy type for use.

    :see: FeatureSet
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the policy.

        The regex pattern for a policy ID string requires "p-" followed by from 8 to 128 lowercase or uppercase letters, digits, or the underscore character (_).

        :stability: experimental
        '''
        ...


class _IPolicyProxy(
    jsii.proxy_for(constructs.IConstruct) # type: ignore[misc]
):
    '''(experimental) Policies in AWS Organizations enable you to apply additional types of management to the AWS accounts in your organization.

    You can use policies when all features are enabled in your organization.

    Before you can create and attach a policy to your organization, you must enable that policy type for use.

    :see: FeatureSet
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IPolicy"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the policy.

        The regex pattern for a policy ID string requires "p-" followed by from 8 to 128 lowercase or uppercase letters, digits, or the underscore character (_).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicy).__jsii_proxy_class__ = lambda : _IPolicyProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IResource")
class IResource(typing_extensions.Protocol):
    '''(experimental) Interface for an AWS Organizations resource.

    :stability: experimental
    '''

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the parent root, organizational unit (OU), account, or policy that you want to create the new OU in.

        :stability: experimental
        '''
        ...


class _IResourceProxy:
    '''(experimental) Interface for an AWS Organizations resource.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IResource"

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the parent root, organizational unit (OU), account, or policy that you want to create the new OU in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IResource).__jsii_proxy_class__ = lambda : _IResourceProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.ITaggableResource")
class ITaggableResource(aws_cdk.ITaggable, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    pass


class _ITaggableResourceProxy(
    jsii.proxy_for(aws_cdk.ITaggable) # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.ITaggableResource"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITaggableResource).__jsii_proxy_class__ = lambda : _ITaggableResourceProxy


@jsii.enum(jsii_type="@pepperize/cdk-organizations.IamUserAccessToBilling")
class IamUserAccessToBilling(enum.Enum):
    '''
    :see: https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/control-access-billing.html#ControllingAccessWebsite-Activate
    :stability: experimental
    '''

    ALLOW = "ALLOW"
    '''(experimental) If set to ALLOW, the new account enables IAM users to access account billing information if they have the required permissions.

    :stability: experimental
    '''
    DENY = "DENY"
    '''(experimental) If set to DENY, only the root user of the new account can access account billing information.

    :stability: experimental
    '''


@jsii.implements(IOrganization)
class Organization(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Organization",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        feature_set: typing.Optional[FeatureSet] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param feature_set: (experimental) Enabling features in your organization. Default: ALL

        :stability: experimental
        '''
        props = OrganizationProps(feature_set=feature_set)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="attachPolicy")
    def attach_policy(self, policy: IPolicy) -> None:
        '''(experimental) Attach a policy.

        Before you can attach the policy, you must enable that policy type for use. You can use policies when you have all features enabled.

        :param policy: -

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "attachPolicy", [policy]))

    @jsii.member(jsii_name="enableAwsServiceAccess")
    def enable_aws_service_access(self, service_principal: builtins.str) -> None:
        '''(experimental) Enables trusted access for a supported AWS service (trusted service), which performs tasks in your organization and its accounts on your behalf.

        :param service_principal: The supported AWS service that you specify.

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "enableAwsServiceAccess", [service_principal]))

    @jsii.member(jsii_name="enablePolicyType")
    def enable_policy_type(self, policy_type: "PolicyType") -> None:
        '''(experimental) Enables policy types in the following two broad categories: Authorization policies and Management policies.

        :param policy_type: : the type of the policy that you specify.

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "enablePolicyType", [policy_type]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="featureSet")
    def feature_set(self) -> FeatureSet:
        '''(experimental) Specifies the functionality that currently is available to the organization.

        If set to "ALL", then all features are enabled and policies can be applied to accounts in the organization. If set to "CONSOLIDATED_BILLING", then only consolidated billing functionality is available.

        :stability: experimental
        '''
        return typing.cast(FeatureSet, jsii.get(self, "featureSet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountArn")
    def management_account_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the account that is designated as the management account for the organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "managementAccountArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountEmail")
    def management_account_email(self) -> builtins.str:
        '''(experimental) The email address that is associated with the AWS account that is designated as the management account for the organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "managementAccountEmail"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementAccountId")
    def management_account_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the management account of an organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "managementAccountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationArn")
    def organization_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of an organization.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationId")
    def organization_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of an organization.

        The regex pattern for an organization ID string requires "o-" followed by from 10 to 32 lowercase letters or digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="root")
    def root(self) -> "Root":
        '''(experimental) The root of the current organization, which is automatically created.

        :stability: experimental
        '''
        return typing.cast("Root", jsii.get(self, "root"))


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.OrganizationProps",
    jsii_struct_bases=[],
    name_mapping={"feature_set": "featureSet"},
)
class OrganizationProps:
    def __init__(self, *, feature_set: typing.Optional[FeatureSet] = None) -> None:
        '''
        :param feature_set: (experimental) Enabling features in your organization. Default: ALL

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if feature_set is not None:
            self._values["feature_set"] = feature_set

    @builtins.property
    def feature_set(self) -> typing.Optional[FeatureSet]:
        '''(experimental) Enabling features in your organization.

        :default: ALL

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_support-all-features.html
        :stability: experimental
        '''
        result = self._values.get("feature_set")
        return typing.cast(typing.Optional[FeatureSet], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.OrganizationalUnitProps",
    jsii_struct_bases=[],
    name_mapping={
        "organizational_unit_name": "organizationalUnitName",
        "parent": "parent",
        "import_on_duplicate": "importOnDuplicate",
        "removal_policy": "removalPolicy",
    },
)
class OrganizationalUnitProps:
    def __init__(
        self,
        *,
        organizational_unit_name: builtins.str,
        parent: "IParent",
        import_on_duplicate: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
    ) -> None:
        '''
        :param organizational_unit_name: (experimental) The friendly name to assign to the new OU.
        :param parent: (experimental) The parent root or OU that you want to create the new OrganizationalUnit in.
        :param import_on_duplicate: (experimental) Whether to import, if a duplicate organizational unit with same name exists in the parent exists. Default: true
        :param removal_policy: (experimental) If set to RemovalPolicy.DESTROY, the organizational unit will be deleted. Default: RemovalPolicy.Retain

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "organizational_unit_name": organizational_unit_name,
            "parent": parent,
        }
        if import_on_duplicate is not None:
            self._values["import_on_duplicate"] = import_on_duplicate
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy

    @builtins.property
    def organizational_unit_name(self) -> builtins.str:
        '''(experimental) The friendly name to assign to the new OU.

        :stability: experimental
        '''
        result = self._values.get("organizational_unit_name")
        assert result is not None, "Required property 'organizational_unit_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def parent(self) -> "IParent":
        '''(experimental) The parent root or OU that you want to create the new OrganizationalUnit in.

        :stability: experimental
        '''
        result = self._values.get("parent")
        assert result is not None, "Required property 'parent' is missing"
        return typing.cast("IParent", result)

    @builtins.property
    def import_on_duplicate(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to import, if a duplicate organizational unit with same name exists in the parent exists.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("import_on_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[aws_cdk.RemovalPolicy]:
        '''(experimental) If set to RemovalPolicy.DESTROY, the organizational unit will be deleted.

        :default: RemovalPolicy.Retain

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[aws_cdk.RemovalPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationalUnitProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.ParentBaseProps",
    jsii_struct_bases=[],
    name_mapping={"child_id": "childId"},
)
class ParentBaseProps:
    def __init__(self, *, child_id: builtins.str) -> None:
        '''
        :param child_id: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "child_id": child_id,
        }

    @builtins.property
    def child_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("child_id")
        assert result is not None, "Required property 'child_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ParentBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.ParentProps",
    jsii_struct_bases=[],
    name_mapping={"child": "child"},
)
class ParentProps:
    def __init__(self, *, child: "IChild") -> None:
        '''
        :param child: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "child": child,
        }

    @builtins.property
    def child(self) -> "IChild":
        '''
        :stability: experimental
        '''
        result = self._values.get("child")
        assert result is not None, "Required property 'child' is missing"
        return typing.cast("IChild", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ParentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IPolicy, ITaggableResource)
class Policy(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Policy",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content: builtins.str,
        policy_name: builtins.str,
        policy_type: "PolicyType",
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param content: (experimental) The policy text content to add to the new policy. The text that you supply must adhere to the rules of the policy type you specify in the Type parameter.
        :param policy_name: (experimental) The friendly name to assign to the policy.
        :param policy_type: (experimental) The type of policy to create. You can specify one of the following values:
        :param description: (experimental) An optional description to assign to the policy.

        :stability: experimental
        '''
        props = PolicyProps(
            content=content,
            policy_name=policy_name,
            policy_type=policy_type,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the policy.

        The regex pattern for a policy ID string requires "p-" followed by from 8 to 128 lowercase or uppercase letters, digits, or the underscore character (_).

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''(experimental) TagManager to set, remove and format tags.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


class PolicyAttachment(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.PolicyAttachment",
):
    '''(experimental) Attaches a policy to a root, an organizational unit (OU), or an individual account.

    How the policy affects accounts depends on the type of policy. Refer to the AWS Organizations User Guide for information about each policy type:

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        policy: IPolicy,
        target: "IPolicyAttachmentTarget",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param policy: (experimental) The policy that you want to attach to the target.
        :param target: (experimental) The root, OU, or account that you want to attach the policy to.

        :stability: experimental
        '''
        props = PolicyAttachmentProps(policy=policy, target=target)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.PolicyAttachmentProps",
    jsii_struct_bases=[],
    name_mapping={"policy": "policy", "target": "target"},
)
class PolicyAttachmentProps:
    def __init__(self, *, policy: IPolicy, target: "IPolicyAttachmentTarget") -> None:
        '''
        :param policy: (experimental) The policy that you want to attach to the target.
        :param target: (experimental) The root, OU, or account that you want to attach the policy to.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "policy": policy,
            "target": target,
        }

    @builtins.property
    def policy(self) -> IPolicy:
        '''(experimental) The policy that you want to attach to the target.

        :stability: experimental
        '''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast(IPolicy, result)

    @builtins.property
    def target(self) -> "IPolicyAttachmentTarget":
        '''(experimental) The root, OU, or account that you want to attach the policy to.

        :stability: experimental
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast("IPolicyAttachmentTarget", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyAttachmentProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.PolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "content": "content",
        "policy_name": "policyName",
        "policy_type": "policyType",
        "description": "description",
    },
)
class PolicyProps:
    def __init__(
        self,
        *,
        content: builtins.str,
        policy_name: builtins.str,
        policy_type: "PolicyType",
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param content: (experimental) The policy text content to add to the new policy. The text that you supply must adhere to the rules of the policy type you specify in the Type parameter.
        :param policy_name: (experimental) The friendly name to assign to the policy.
        :param policy_type: (experimental) The type of policy to create. You can specify one of the following values:
        :param description: (experimental) An optional description to assign to the policy.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "content": content,
            "policy_name": policy_name,
            "policy_type": policy_type,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def content(self) -> builtins.str:
        '''(experimental) The policy text content to add to the new policy.

        The text that you supply must adhere to the rules of the policy type you specify in the Type parameter.

        :stability: experimental
        '''
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_name(self) -> builtins.str:
        '''(experimental) The friendly name to assign to the policy.

        :stability: experimental
        '''
        result = self._values.get("policy_name")
        assert result is not None, "Required property 'policy_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy_type(self) -> "PolicyType":
        '''(experimental) The type of policy to create.

        You can specify one of the following values:

        :stability: experimental
        '''
        result = self._values.get("policy_type")
        assert result is not None, "Required property 'policy_type' is missing"
        return typing.cast("PolicyType", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) An optional description to assign to the policy.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@pepperize/cdk-organizations.PolicyType")
class PolicyType(enum.Enum):
    '''(experimental) Organizations offers policy types in the following two broad categories:       Authorization policies help you to centrally manage the security of the AWS accounts in your organization.      Management policies enable you to centrally configure and manage AWS services and their features. .

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html#orgs-policy-types
    :stability: experimental
    '''

    SERVICE_CONTROL_POLICY = "SERVICE_CONTROL_POLICY"
    '''(experimental) Service control policies (SCPs) offer central control over the maximum available permissions for all of the accounts in your organization.

    :stability: experimental
    '''
    TAG_POLICY = "TAG_POLICY"
    '''(experimental) Tag policies help you standardize the tags attached to the AWS resources in your organization's accounts.

    :stability: experimental
    '''
    BACKUP_POLICY = "BACKUP_POLICY"
    '''(experimental) Backup policies help you centrally manage and apply backup plans to the AWS resources across your organization's accounts.

    :stability: experimental
    '''
    AISERVICES_OPT_OUT_POLICY = "AISERVICES_OPT_OUT_POLICY"
    '''(experimental) Artificial Intelligence (AI) services opt-out policies enable you to control data collection for AWS AI services for all of your organization's accounts.

    :stability: experimental
    '''


class TagResource(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.TagResource",
):
    '''(experimental) Add tags to an AWS Organizations resource to make it easier to identify, organize, and search.

    :see: https://docs.aws.amazon.com/ARG/latest/APIReference/API_Tag.html
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        resource_id: builtins.str,
        tags: aws_cdk.IResolvable,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param resource_id: 
        :param tags: 

        :stability: experimental
        '''
        props = TagResourceProps(resource_id=resource_id, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@pepperize/cdk-organizations.TagResourceProps",
    jsii_struct_bases=[],
    name_mapping={"resource_id": "resourceId", "tags": "tags"},
)
class TagResourceProps:
    def __init__(self, *, resource_id: builtins.str, tags: aws_cdk.IResolvable) -> None:
        '''
        :param resource_id: 
        :param tags: 

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "resource_id": resource_id,
            "tags": tags,
        }

    @builtins.property
    def resource_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("resource_id")
        assert result is not None, "Required property 'resource_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tags(self) -> aws_cdk.IResolvable:
        '''
        :stability: experimental
        '''
        result = self._values.get("tags")
        assert result is not None, "Required property 'tags' is missing"
        return typing.cast(aws_cdk.IResolvable, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TagResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Validators(
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Validators",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls) -> "Validators":
        '''
        :stability: experimental
        '''
        return typing.cast("Validators", jsii.sinvoke(cls, "of", []))

    @jsii.member(jsii_name="accountId")
    def account_id(self, id: builtins.str) -> builtins.bool:
        '''
        :param id: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "accountId", [id]))

    @jsii.member(jsii_name="accountName")
    def account_name(self, name: builtins.str) -> builtins.bool:
        '''
        :param name: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "accountName", [name]))

    @jsii.member(jsii_name="email")
    def email(self, email: builtins.str) -> builtins.bool:
        '''
        :param email: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "email", [email]))

    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self, name: builtins.str) -> builtins.bool:
        '''
        :param name: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "organizationalUnitName", [name]))

    @jsii.member(jsii_name="policyContent")
    def policy_content(self, content: builtins.str) -> builtins.bool:
        '''
        :param content: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "policyContent", [content]))

    @jsii.member(jsii_name="servicePrincipal")
    def service_principal(self, service_principal: builtins.str) -> builtins.bool:
        '''
        :param service_principal: -

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "servicePrincipal", [service_principal]))


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IChild")
class IChild(constructs.IConstruct, IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    pass


class _IChildProxy(
    jsii.proxy_for(constructs.IConstruct), # type: ignore[misc]
    jsii.proxy_for(IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IChild"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IChild).__jsii_proxy_class__ = lambda : _IChildProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IParent")
class IParent(constructs.IConstruct, IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    pass


class _IParentProxy(
    jsii.proxy_for(constructs.IConstruct), # type: ignore[misc]
    jsii.proxy_for(IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IParent"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IParent).__jsii_proxy_class__ = lambda : _IParentProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IPolicyAttachmentTarget")
class IPolicyAttachmentTarget(
    constructs.IDependable,
    IResource,
    typing_extensions.Protocol,
):
    '''
    :stability: experimental
    '''

    pass


class _IPolicyAttachmentTargetProxy(
    jsii.proxy_for(constructs.IDependable), # type: ignore[misc]
    jsii.proxy_for(IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IPolicyAttachmentTarget"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IPolicyAttachmentTarget).__jsii_proxy_class__ = lambda : _IPolicyAttachmentTargetProxy


@jsii.implements(IParent)
class ParentBase(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@pepperize/cdk-organizations.ParentBase",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        child_id: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param child_id: 

        :stability: experimental
        '''
        props = ParentBaseProps(child_id=child_id)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the parent root, organizational unit (OU), account, or policy that you want to create the new OU in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="parentId")
    def parent_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "parentId"))


class _ParentBaseProxy(ParentBase):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ParentBase).__jsii_proxy_class__ = lambda : _ParentBaseProxy


@jsii.implements(IParent, IPolicyAttachmentTarget, ITaggableResource)
class Root(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Root",
):
    '''(experimental) The parent container for all the accounts for your organization.

    If you apply a policy to the root, it applies to all organizational units (OUs) and accounts in the organization.
    Currently, you can have only one root. AWS Organizations automatically creates it for you when you create an organization.

    :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html
    :stability: experimental
    '''

    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="attachPolicy")
    def attach_policy(self, policy: IPolicy) -> None:
        '''(experimental) Attach a policy.

        Before you can attach the policy, you must enable that policy type for use. You can use policies when you have all features enabled.

        :param policy: -

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "attachPolicy", [policy]))

    @jsii.member(jsii_name="enablePolicyType")
    def enable_policy_type(self, policy_type: PolicyType) -> None:
        '''(experimental) Enables and disables Enables a policy type.

        After you enable a policy type in a root, you can attach policies of that type to the root, any organizational unit (OU), or account in that root.

        :param policy_type: -

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_enable-disable.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "enablePolicyType", [policy_type]))

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the parent root, organizational unit (OU), account, or policy that you want to create the new OU in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def _resource(self) -> aws_cdk.custom_resources.AwsCustomResource:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.custom_resources.AwsCustomResource, jsii.get(self, "resource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rootId")
    def root_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) for the root.

        The regex pattern for a root ID string requires "r-" followed by from 4 to 32 lowercase letters or digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "rootId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''(experimental) TagManager to set, remove and format tags.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IAccount")
class IAccount(
    IPolicyAttachmentTarget,
    IChild,
    constructs.IConstruct,
    IResource,
    typing_extensions.Protocol,
):
    '''
    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountArn")
    def account_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the account.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''(experimental) If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''(experimental) The friendly name of the account.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''(experimental) The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="delegateAdministrator")
    def delegate_administrator(self, service_principal: builtins.str) -> None:
        '''(experimental) Enables trusted access for the AWS service (trusted service) as Delegated Administrator, which performs tasks in your organization and its accounts on your behalf.

        :param service_principal: The supported AWS service that you specify.

        :stability: experimental
        '''
        ...


class _IAccountProxy(
    jsii.proxy_for(IPolicyAttachmentTarget), # type: ignore[misc]
    jsii.proxy_for(IChild), # type: ignore[misc]
    jsii.proxy_for(constructs.IConstruct), # type: ignore[misc]
    jsii.proxy_for(IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IAccount"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountArn")
    def account_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the account.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''(experimental) If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''(experimental) The friendly name of the account.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''(experimental) The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @jsii.member(jsii_name="delegateAdministrator")
    def delegate_administrator(self, service_principal: builtins.str) -> None:
        '''(experimental) Enables trusted access for the AWS service (trusted service) as Delegated Administrator, which performs tasks in your organization and its accounts on your behalf.

        :param service_principal: The supported AWS service that you specify.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "delegateAdministrator", [service_principal]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAccount).__jsii_proxy_class__ = lambda : _IAccountProxy


@jsii.interface(jsii_type="@pepperize/cdk-organizations.IOrganizationalUnit")
class IOrganizationalUnit(
    IPolicyAttachmentTarget,
    IParent,
    IChild,
    constructs.IConstruct,
    typing_extensions.Protocol,
):
    '''(experimental) A container for accounts within a root.

    An OU also can contain other OUs, enabling you to create a hierarchy that resembles an upside-down tree, with a root at the top and branches of OUs that reach down, ending in accounts that are the leaves of the tree. When you attach a policy to one of the nodes in the hierarchy, it flows down and affects all the branches (OUs) and leaves (accounts) beneath it. An OU can have exactly one parent, and currently each account can be a member of exactly one OU.

    You must first move all accounts out of the OU and any child OUs, and then you can delete the child OUs.

    :stability: experimental
    '''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.

        :stability: experimental
        '''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''(experimental) The friendly name of this OU.

        :stability: experimental
        '''
        ...


class _IOrganizationalUnitProxy(
    jsii.proxy_for(IPolicyAttachmentTarget), # type: ignore[misc]
    jsii.proxy_for(IParent), # type: ignore[misc]
    jsii.proxy_for(IChild), # type: ignore[misc]
    jsii.proxy_for(constructs.IConstruct), # type: ignore[misc]
):
    '''(experimental) A container for accounts within a root.

    An OU also can contain other OUs, enabling you to create a hierarchy that resembles an upside-down tree, with a root at the top and branches of OUs that reach down, ending in accounts that are the leaves of the tree. When you attach a policy to one of the nodes in the hierarchy, it flows down and affects all the branches (OUs) and leaves (accounts) beneath it. An OU can have exactly one parent, and currently each account can be a member of exactly one OU.

    You must first move all accounts out of the OU and any child OUs, and then you can delete the child OUs.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@pepperize/cdk-organizations.IOrganizationalUnit"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''(experimental) The friendly name of this OU.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOrganizationalUnit).__jsii_proxy_class__ = lambda : _IOrganizationalUnitProxy


@jsii.implements(IOrganizationalUnit, ITaggableResource)
class OrganizationalUnit(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.OrganizationalUnit",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        organizational_unit_name: builtins.str,
        parent: IParent,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param organizational_unit_name: (experimental) The friendly name to assign to the new OU.
        :param parent: (experimental) The parent root or OU that you want to create the new OrganizationalUnit in.
        :param import_on_duplicate: (experimental) Whether to import, if a duplicate organizational unit with same name exists in the parent exists. Default: true
        :param removal_policy: (experimental) If set to RemovalPolicy.DESTROY, the organizational unit will be deleted. Default: RemovalPolicy.Retain

        :stability: experimental
        '''
        props = OrganizationalUnitProps(
            organizational_unit_name=organizational_unit_name,
            parent=parent,
            import_on_duplicate=import_on_duplicate,
            removal_policy=removal_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="attachPolicy")
    def attach_policy(self, policy: IPolicy) -> None:
        '''(experimental) Attach a policy.

        Before you can attach the policy, you must enable that policy type for use. You can use policies when you have all features enabled.

        :param policy: -

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "attachPolicy", [policy]))

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the parent root, organizational unit (OU), account, or policy that you want to create the new OU in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitArn")
    def organizational_unit_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of this OU.

        For more information about ARNs in Organizations, see `ARN Formats Supported by Organizations <https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsorganizations.html#awsorganizations-resources-for-iam-policies>`_ in the AWS Service Authorization Reference.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitId")
    def organizational_unit_id(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) associated with this OU.

        The regex pattern for an organizational unit ID string requires "ou-" followed by from 4 to 32 lowercase letters or digits (the ID of the root that contains the OU). This string is followed by a second "-" dash and from 8 to 32 additional lowercase letters or digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitName")
    def organizational_unit_name(self) -> builtins.str:
        '''(experimental) The friendly name of this OU.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnitName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def _resource(self) -> aws_cdk.CustomResource:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "resource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''(experimental) TagManager to set, remove and format tags.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


class Parent(
    ParentBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Parent",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        child: IChild,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param child: 

        :stability: experimental
        '''
        props = ParentProps(child=child)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromChildId") # type: ignore[misc]
    @builtins.classmethod
    def from_child_id(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        child_id: builtins.str,
    ) -> IParent:
        '''
        :param scope: -
        :param id: -
        :param child_id: -

        :stability: experimental
        '''
        return typing.cast(IParent, jsii.sinvoke(cls, "fromChildId", [scope, id, child_id]))


@jsii.implements(IAccount, ITaggableResource)
class Account(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@pepperize/cdk-organizations.Account",
):
    '''(experimental) Creates or imports an AWS account that is automatically a member of the organization whose credentials made the request.

    AWS Organizations automatically copies the information from the management account to the new member account

    :stability: experimental
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        account_name: builtins.str,
        email: builtins.str,
        iam_user_access_to_billing: typing.Optional[IamUserAccessToBilling] = None,
        import_on_duplicate: typing.Optional[builtins.bool] = None,
        parent: typing.Optional[IParent] = None,
        removal_policy: typing.Optional[aws_cdk.RemovalPolicy] = None,
        role_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account_name: (experimental) The friendly name of the member account.
        :param email: (experimental) The email address of the owner to assign to the new member account. This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.
        :param iam_user_access_to_billing: (experimental) If set to ALLOW , the new account enables IAM users to access account billing information if they have the required permissions. If set to DENY , only the root user of the new account can access account billing information. Default: ALLOW
        :param import_on_duplicate: (experimental) Whether to import, if a duplicate account with same name and email already exists. Default: true
        :param parent: (experimental) The parent root or OU that you want to create the new Account in.
        :param removal_policy: (experimental) If set to RemovalPolicy.DESTROY, the account will be moved to the root. Default: RemovalPolicy.Retain
        :param role_name: (experimental) The name of an IAM role that AWS Organizations automatically preconfigures in the new member account. This role trusts the management account, allowing users in the management account to assume the role, as permitted by the management account administrator. The role has administrator permissions in the new member account. If you don't specify this parameter, the role name defaults to OrganizationAccountAccessRole.

        :stability: experimental
        '''
        props = AccountProps(
            account_name=account_name,
            email=email,
            iam_user_access_to_billing=iam_user_access_to_billing,
            import_on_duplicate=import_on_duplicate,
            parent=parent,
            removal_policy=removal_policy,
            role_name=role_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="attachPolicy")
    def attach_policy(self, policy: IPolicy) -> None:
        '''(experimental) Attach a policy.

        Before you can attach the policy, you must enable that policy type for use. You can use policies when you have all features enabled.

        :param policy: -

        :see: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies.html
        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "attachPolicy", [policy]))

    @jsii.member(jsii_name="delegateAdministrator")
    def delegate_administrator(self, service_principal: builtins.str) -> None:
        '''(experimental) Enables trusted access for the AWS service (trusted service) as Delegated Administrator, which performs tasks in your organization and its accounts on your behalf.

        :param service_principal: The supported AWS service that you specify.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "delegateAdministrator", [service_principal]))

    @jsii.member(jsii_name="identifier")
    def identifier(self) -> builtins.str:
        '''(experimental) The unique identifier (ID) of the parent root, organizational unit (OU), account, or policy that you want to create the new OU in.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "identifier", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountArn")
    def account_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the account.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        '''(experimental) If the account was created successfully, the unique identifier (ID) of the new account.

        Exactly 12 digits.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accountName")
    def account_name(self) -> builtins.str:
        '''(experimental) The friendly name of the account.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "accountName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="email")
    def email(self) -> builtins.str:
        '''(experimental) The email address of the owner to assign to the new member account.

        This email address must not already be associated with another AWS account. You must use a valid email address to complete account creation. You can't access the root user of the account or remove an account that was created with an invalid email address.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "email"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resource")
    def _resource(self) -> aws_cdk.CustomResource:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.CustomResource, jsii.get(self, "resource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.TagManager:
        '''(experimental) TagManager to set, remove and format tags.

        :stability: experimental
        '''
        return typing.cast(aws_cdk.TagManager, jsii.get(self, "tags"))


__all__ = [
    "Account",
    "AccountProps",
    "DelegatedAdministrator",
    "DelegatedAdministratorProps",
    "EnableAwsServiceAccess",
    "EnableAwsServiceAccessProps",
    "EnablePolicyType",
    "EnablePolicyTypeProps",
    "FeatureSet",
    "IAccount",
    "IChild",
    "IOrganization",
    "IOrganizationalUnit",
    "IParent",
    "IPolicy",
    "IPolicyAttachmentTarget",
    "IResource",
    "ITaggableResource",
    "IamUserAccessToBilling",
    "Organization",
    "OrganizationProps",
    "OrganizationalUnit",
    "OrganizationalUnitProps",
    "Parent",
    "ParentBase",
    "ParentBaseProps",
    "ParentProps",
    "Policy",
    "PolicyAttachment",
    "PolicyAttachmentProps",
    "PolicyProps",
    "PolicyType",
    "Root",
    "TagResource",
    "TagResourceProps",
    "Validators",
]

publication.publish()
