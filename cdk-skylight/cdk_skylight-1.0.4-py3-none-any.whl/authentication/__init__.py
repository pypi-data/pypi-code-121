import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk.aws_directoryservice
import aws_cdk.aws_ec2
import aws_cdk.aws_secretsmanager
import constructs
from ..compute import DomainWindowsNode as _DomainWindowsNode_bbfd2a18


class AwsManagedMicrosoftAd(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-skylight.authentication.AwsManagedMicrosoftAd",
):
    '''A Ad Authentication represents an integration pattern of Managed AD and Route 53 Resolver in a specific VPC.

    The Construct creates Managed AD with the provided Secret (Secrets Manager) or generates a new Secret.
    The secret saved to SSM parameter store so others can use it with other Constructs (Such as Windows node or FSx)
    The provided VPC or the new created VPC will be configured to forward DNS requests to the Managed AD with Route53 Resolvers
    The construct also creates (optionally) t3.nano machine that is part of the domain that can be used to run admin-tasks (such as createADGroup)

    The createADGroup() method creates an Active Directory permission group in the domain, using the domain admin user.
    Please note: When calling createADGroup() API, a Lambda will be created to start the worker machine (Using AWS-SDK),
    then each command will be scheduled with State Manager, and the instance will be shut down after complete.
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "IAwsManagedMicrosoftAdProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createADGroup")
    def create_ad_group(
        self,
        group_name: builtins.str,
        group_description: builtins.str,
    ) -> None:
        '''
        :param group_name: -
        :param group_description: -
        '''
        return typing.cast(None, jsii.invoke(self, "createADGroup", [group_name, group_description]))

    @jsii.member(jsii_name="createServiceAccount")
    def create_service_account(
        self,
        ad_service_account_name: builtins.str,
        service_principal_names: builtins.str,
        principals_allowed_to_retrieve_managed_password: builtins.str,
    ) -> None:
        '''
        :param ad_service_account_name: -
        :param service_principal_names: -
        :param principals_allowed_to_retrieve_managed_password: -
        '''
        return typing.cast(None, jsii.invoke(self, "createServiceAccount", [ad_service_account_name, service_principal_names, principals_allowed_to_retrieve_managed_password]))

    @jsii.member(jsii_name="createWorker")
    def create_worker(
        self,
        domain_name: builtins.str,
        domain_password: aws_cdk.aws_secretsmanager.ISecret,
    ) -> _DomainWindowsNode_bbfd2a18:
        '''
        :param domain_name: -
        :param domain_password: -
        '''
        return typing.cast(_DomainWindowsNode_bbfd2a18, jsii.invoke(self, "createWorker", [domain_name, domain_password]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="adParameters")
    def ad_parameters(self) -> "IAwsManagedMicrosoftAdParameters":
        return typing.cast("IAwsManagedMicrosoftAdParameters", jsii.get(self, "adParameters"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="microsoftAD")
    def microsoft_ad(self) -> aws_cdk.aws_directoryservice.CfnMicrosoftAD:
        return typing.cast(aws_cdk.aws_directoryservice.CfnMicrosoftAD, jsii.get(self, "microsoftAD"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "IAwsManagedMicrosoftAdProps":
        return typing.cast("IAwsManagedMicrosoftAdProps", jsii.get(self, "props"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> aws_cdk.aws_secretsmanager.ISecret:
        return typing.cast(aws_cdk.aws_secretsmanager.ISecret, jsii.get(self, "secret"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainWindowsNode")
    def domain_windows_node(self) -> typing.Optional[_DomainWindowsNode_bbfd2a18]:
        return typing.cast(typing.Optional[_DomainWindowsNode_bbfd2a18], jsii.get(self, "domainWindowsNode"))


@jsii.enum(
    jsii_type="cdk-skylight.authentication.AwsManagedMicrosoftConfigurationStoreType"
)
class AwsManagedMicrosoftConfigurationStoreType(enum.Enum):
    SSM = "SSM"


@jsii.interface(
    jsii_type="cdk-skylight.authentication.IAwsManagedMicrosoftAdParameters"
)
class IAwsManagedMicrosoftAdParameters(typing_extensions.Protocol):
    '''The properties of an DomainWindowsNodeProps, requires Active Directory parameter to read the Secret to join the domain Default setting: Domain joined, m5.2xlarge, latest windows, Managed by SSM.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationStoreType")
    def configuration_store_type(
        self,
    ) -> typing.Optional[AwsManagedMicrosoftConfigurationStoreType]:
        '''The name of the Configuration Store Type to use.

        :default: - 'AWS Systems Manager Parameter Store'.
        '''
        ...

    @configuration_store_type.setter
    def configuration_store_type(
        self,
        value: typing.Optional[AwsManagedMicrosoftConfigurationStoreType],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIDPointer")
    def directory_id_pointer(self) -> typing.Optional[builtins.str]:
        '''The name of the SSM Object that contains the Directory ID.

        :default: - 'directoryID'.
        '''
        ...

    @directory_id_pointer.setter
    def directory_id_pointer(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The SSM namespace to read/write parameters to.

        :default: - 'cdk-skylight'.
        '''
        ...

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretPointer")
    def secret_pointer(self) -> typing.Optional[builtins.str]:
        '''The name of the SSM Object that contains the secret name in Secrets Manager.

        :default: - 'domain-secret'.
        '''
        ...

    @secret_pointer.setter
    def secret_pointer(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IAwsManagedMicrosoftAdParametersProxy:
    '''The properties of an DomainWindowsNodeProps, requires Active Directory parameter to read the Secret to join the domain Default setting: Domain joined, m5.2xlarge, latest windows, Managed by SSM.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.authentication.IAwsManagedMicrosoftAdParameters"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationStoreType")
    def configuration_store_type(
        self,
    ) -> typing.Optional[AwsManagedMicrosoftConfigurationStoreType]:
        '''The name of the Configuration Store Type to use.

        :default: - 'AWS Systems Manager Parameter Store'.
        '''
        return typing.cast(typing.Optional[AwsManagedMicrosoftConfigurationStoreType], jsii.get(self, "configurationStoreType"))

    @configuration_store_type.setter
    def configuration_store_type(
        self,
        value: typing.Optional[AwsManagedMicrosoftConfigurationStoreType],
    ) -> None:
        jsii.set(self, "configurationStoreType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryIDPointer")
    def directory_id_pointer(self) -> typing.Optional[builtins.str]:
        '''The name of the SSM Object that contains the Directory ID.

        :default: - 'directoryID'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryIDPointer"))

    @directory_id_pointer.setter
    def directory_id_pointer(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "directoryIDPointer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The SSM namespace to read/write parameters to.

        :default: - 'cdk-skylight'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "namespace", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretPointer")
    def secret_pointer(self) -> typing.Optional[builtins.str]:
        '''The name of the SSM Object that contains the secret name in Secrets Manager.

        :default: - 'domain-secret'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretPointer"))

    @secret_pointer.setter
    def secret_pointer(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "secretPointer", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAwsManagedMicrosoftAdParameters).__jsii_proxy_class__ = lambda : _IAwsManagedMicrosoftAdParametersProxy


@jsii.interface(jsii_type="cdk-skylight.authentication.IAwsManagedMicrosoftAdProps")
class IAwsManagedMicrosoftAdProps(typing_extensions.Protocol):
    '''The properties for the AwsManagedMicrosoftAd class.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use, must have private subnets.'''
        ...

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationStore")
    def configuration_store(self) -> typing.Optional[IAwsManagedMicrosoftAdParameters]:
        '''The configuration store to save the directory parameters (After deployed).'''
        ...

    @configuration_store.setter
    def configuration_store(
        self,
        value: typing.Optional[IAwsManagedMicrosoftAdParameters],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createWorker")
    def create_worker(self) -> typing.Optional[builtins.bool]:
        '''Create Domain joined machine to be used to run Powershell commands to that directory.

        (i.e Create Ad Group)

        :default: - 'true'.
        '''
        ...

    @create_worker.setter
    def create_worker(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name for the Active Directory Domain.

        :default: - 'domain.aws'.
        '''
        ...

    @domain_name.setter
    def domain_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="edition")
    def edition(self) -> typing.Optional[builtins.str]:
        '''The edition to use for the Active Directory Domain.

        Allowed values: Enterprise | Standard
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-edition

        :default: - 'Standard'.
        '''
        ...

    @edition.setter
    def edition(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''The secrets manager secret to use must be in format: '{Domain: <domain.name>, UserID: 'Admin', Password: ''}'.

        :default: - 'Randomly generated and stored in Secret Manager'.
        '''
        ...

    @secret.setter
    def secret(
        self,
        value: typing.Optional[aws_cdk.aws_secretsmanager.ISecret],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''The secret name to save the Domain Admin object.

        :default: - '<domain.name>-secret'.
        '''
        ...

    @secret_name.setter
    def secret_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SelectedSubnets]:
        '''VPC subnet selection, subnets must be private and exactly 2.'''
        ...

    @vpc_subnets.setter
    def vpc_subnets(
        self,
        value: typing.Optional[aws_cdk.aws_ec2.SelectedSubnets],
    ) -> None:
        ...


class _IAwsManagedMicrosoftAdPropsProxy:
    '''The properties for the AwsManagedMicrosoftAd class.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.authentication.IAwsManagedMicrosoftAdProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use, must have private subnets.'''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        jsii.set(self, "vpc", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationStore")
    def configuration_store(self) -> typing.Optional[IAwsManagedMicrosoftAdParameters]:
        '''The configuration store to save the directory parameters (After deployed).'''
        return typing.cast(typing.Optional[IAwsManagedMicrosoftAdParameters], jsii.get(self, "configurationStore"))

    @configuration_store.setter
    def configuration_store(
        self,
        value: typing.Optional[IAwsManagedMicrosoftAdParameters],
    ) -> None:
        jsii.set(self, "configurationStore", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createWorker")
    def create_worker(self) -> typing.Optional[builtins.bool]:
        '''Create Domain joined machine to be used to run Powershell commands to that directory.

        (i.e Create Ad Group)

        :default: - 'true'.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "createWorker"))

    @create_worker.setter
    def create_worker(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "createWorker", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''The domain name for the Active Directory Domain.

        :default: - 'domain.aws'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="edition")
    def edition(self) -> typing.Optional[builtins.str]:
        '''The edition to use for the Active Directory Domain.

        Allowed values: Enterprise | Standard
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-directoryservice-microsoftad.html#cfn-directoryservice-microsoftad-edition

        :default: - 'Standard'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "edition"))

    @edition.setter
    def edition(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "edition", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        '''The secrets manager secret to use must be in format: '{Domain: <domain.name>, UserID: 'Admin', Password: ''}'.

        :default: - 'Randomly generated and stored in Secret Manager'.
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], jsii.get(self, "secret"))

    @secret.setter
    def secret(
        self,
        value: typing.Optional[aws_cdk.aws_secretsmanager.ISecret],
    ) -> None:
        jsii.set(self, "secret", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''The secret name to save the Domain Admin object.

        :default: - '<domain.name>-secret'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "secretName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> typing.Optional[aws_cdk.aws_ec2.SelectedSubnets]:
        '''VPC subnet selection, subnets must be private and exactly 2.'''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.SelectedSubnets], jsii.get(self, "vpcSubnets"))

    @vpc_subnets.setter
    def vpc_subnets(
        self,
        value: typing.Optional[aws_cdk.aws_ec2.SelectedSubnets],
    ) -> None:
        jsii.set(self, "vpcSubnets", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAwsManagedMicrosoftAdProps).__jsii_proxy_class__ = lambda : _IAwsManagedMicrosoftAdPropsProxy


__all__ = [
    "AwsManagedMicrosoftAd",
    "AwsManagedMicrosoftConfigurationStoreType",
    "IAwsManagedMicrosoftAdParameters",
    "IAwsManagedMicrosoftAdProps",
]

publication.publish()
