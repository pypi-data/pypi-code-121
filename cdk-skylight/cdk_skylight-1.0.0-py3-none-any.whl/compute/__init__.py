import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk.aws_autoscaling
import aws_cdk.aws_ec2
import aws_cdk.aws_eks
import aws_cdk.aws_iam
import aws_cdk.aws_secretsmanager
import constructs
from ..authentication import (
    IAwsManagedMicrosoftAdParameters as _IAwsManagedMicrosoftAdParameters_42a8ccd6
)
from ..storage import IFSxWindowsParameters as _IFSxWindowsParameters_64d66ceb


class DomainWindowsNode(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-skylight.compute.DomainWindowsNode",
):
    '''A Domain Windows Node represents one Windows EC2 instance configured with Active Directory.

    The DomainWindowsNode can be customized to different instance sizes and additional permissions set just like any other EC2 Instance.
    You can use this construct to run elevated domain tasks with domain permissions or run your application in a single instance setup.

    The machine will be joined to the provided Active Directory domain using a custom CloudFormation bootstrap that will wait until the required reboot to join the domain. Then it will register the machine in SSM and pull tasks from the SSM State manager.

    You can send tasks to that machine using the provided methods: runPsCommands() and runPSwithDomainAdmin()
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "IDomainWindowsNodeProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="openRDP")
    def open_rdp(self, ipaddress: builtins.str) -> None:
        '''Open the security group of the Node Node to specific IP address on port 3389 i.e: openRDP("1.1.1.1/32").

        :param ipaddress: -
        '''
        return typing.cast(None, jsii.invoke(self, "openRDP", [ipaddress]))

    @jsii.member(jsii_name="runPsCommands")
    def run_ps_commands(
        self,
        ps_commands: typing.Sequence[builtins.str],
        id: builtins.str,
    ) -> None:
        '''Running PowerShell scripts on the Node with SSM Document.

        i.e: runPsCommands(["Write-host 'Hello world'", "Write-host 'Second command'"], "myScript")

        :param ps_commands: -
        :param id: -
        '''
        return typing.cast(None, jsii.invoke(self, "runPsCommands", [ps_commands, id]))

    @jsii.member(jsii_name="runPSwithDomainAdmin")
    def run_p_swith_domain_admin(
        self,
        ps_commands: typing.Sequence[builtins.str],
        id: builtins.str,
    ) -> None:
        '''Running PowerShell scripts on the Node with SSM Document with Domain Admin (Using the Secret used to join the machine to the domain) i.e: runPsCommands(["Write-host 'Hello world'", "Write-host 'Second command'"], "myScript") The provided psCommands will be stored in C:\\Scripts and will be run with scheduled task with Domain Admin rights.

        :param ps_commands: -
        :param id: -
        '''
        return typing.cast(None, jsii.invoke(self, "runPSwithDomainAdmin", [ps_commands, id]))

    @jsii.member(jsii_name="runShellCommands")
    def run_shell_commands(
        self,
        shell_commands: typing.Sequence[builtins.str],
        id: builtins.str,
    ) -> None:
        '''Running bash scripts on the Node with SSM Document.

        i.e: runPsCommands(["echo 'hello world'", "echo 'Second command'"], "myScript")

        :param shell_commands: -
        :param id: -
        '''
        return typing.cast(None, jsii.invoke(self, "runShellCommands", [shell_commands, id]))

    @jsii.member(jsii_name="startInstance")
    def start_instance(self) -> None:
        return typing.cast(None, jsii.invoke(self, "startInstance", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instance")
    def instance(self) -> aws_cdk.aws_ec2.Instance:
        return typing.cast(aws_cdk.aws_ec2.Instance, jsii.get(self, "instance"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodeRole")
    def node_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "nodeRole"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordObject")
    def password_object(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], jsii.get(self, "passwordObject"))


@jsii.interface(jsii_type="cdk-skylight.compute.IDomainWindowsNodeProps")
class IDomainWindowsNodeProps(typing_extensions.Protocol):
    '''The properties of an DomainWindowsNodeProps, requires Active Directory parameter to read the Secret to join the domain Default setting: Domain joined, m5.2xlarge, latest windows, Managed by SSM.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use.'''
        ...

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiName")
    def ami_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AMI to search in SSM (ec2.LookupNodeImage) supports Regex.

        :default: - 'Windows_Server-2022-English-Full'
        '''
        ...

    @ami_name.setter
    def ami_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[builtins.str]:
        ...

    @domain_name.setter
    def domain_name(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamManagedPoliciesList")
    def iam_managed_policies_list(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.IManagedPolicy]]:
        '''IAM Instance role permissions.

        :default: - 'AmazonSSMManagedInstanceCore, AmazonSSMDirectoryServiceAccess'.
        '''
        ...

    @iam_managed_policies_list.setter
    def iam_managed_policies_list(
        self,
        value: typing.Optional[typing.List[aws_cdk.aws_iam.IManagedPolicy]],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[builtins.str]:
        '''The EC2 Instance type to use.

        :default: - 'm5.2xlarge'.
        '''
        ...

    @instance_type.setter
    def instance_type(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordObject")
    def password_object(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        ...

    @password_object.setter
    def password_object(
        self,
        value: typing.Optional[aws_cdk.aws_secretsmanager.ISecret],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usePrivateSubnet")
    def use_private_subnet(self) -> typing.Optional[builtins.bool]:
        '''Choose if to launch the instance in Private or in Public subnet Private = Subnet that routes to the internet, but not vice versa.

        Public = Subnet that routes to the internet and vice versa.

        :default: - Private.
        '''
        ...

    @use_private_subnet.setter
    def use_private_subnet(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userData")
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default: - 'undefined'
        '''
        ...

    @user_data.setter
    def user_data(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowsMachine")
    def windows_machine(self) -> typing.Optional[builtins.bool]:
        '''
        :default: - 'true'
        '''
        ...

    @windows_machine.setter
    def windows_machine(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IDomainWindowsNodePropsProxy:
    '''The properties of an DomainWindowsNodeProps, requires Active Directory parameter to read the Secret to join the domain Default setting: Domain joined, m5.2xlarge, latest windows, Managed by SSM.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.compute.IDomainWindowsNodeProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use.'''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        jsii.set(self, "vpc", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="amiName")
    def ami_name(self) -> typing.Optional[builtins.str]:
        '''The name of the AMI to search in SSM (ec2.LookupNodeImage) supports Regex.

        :default: - 'Windows_Server-2022-English-Full'
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amiName"))

    @ami_name.setter
    def ami_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "amiName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="iamManagedPoliciesList")
    def iam_managed_policies_list(
        self,
    ) -> typing.Optional[typing.List[aws_cdk.aws_iam.IManagedPolicy]]:
        '''IAM Instance role permissions.

        :default: - 'AmazonSSMManagedInstanceCore, AmazonSSMDirectoryServiceAccess'.
        '''
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.IManagedPolicy]], jsii.get(self, "iamManagedPoliciesList"))

    @iam_managed_policies_list.setter
    def iam_managed_policies_list(
        self,
        value: typing.Optional[typing.List[aws_cdk.aws_iam.IManagedPolicy]],
    ) -> None:
        jsii.set(self, "iamManagedPoliciesList", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[builtins.str]:
        '''The EC2 Instance type to use.

        :default: - 'm5.2xlarge'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="passwordObject")
    def password_object(self) -> typing.Optional[aws_cdk.aws_secretsmanager.ISecret]:
        return typing.cast(typing.Optional[aws_cdk.aws_secretsmanager.ISecret], jsii.get(self, "passwordObject"))

    @password_object.setter
    def password_object(
        self,
        value: typing.Optional[aws_cdk.aws_secretsmanager.ISecret],
    ) -> None:
        jsii.set(self, "passwordObject", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usePrivateSubnet")
    def use_private_subnet(self) -> typing.Optional[builtins.bool]:
        '''Choose if to launch the instance in Private or in Public subnet Private = Subnet that routes to the internet, but not vice versa.

        Public = Subnet that routes to the internet and vice versa.

        :default: - Private.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "usePrivateSubnet"))

    @use_private_subnet.setter
    def use_private_subnet(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "usePrivateSubnet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userData")
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default: - 'undefined'
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "userData", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowsMachine")
    def windows_machine(self) -> typing.Optional[builtins.bool]:
        '''
        :default: - 'true'
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "windowsMachine"))

    @windows_machine.setter
    def windows_machine(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "windowsMachine", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomainWindowsNodeProps).__jsii_proxy_class__ = lambda : _IDomainWindowsNodePropsProxy


@jsii.interface(jsii_type="cdk-skylight.compute.IRuntimeNodes")
class IRuntimeNodes(typing_extensions.Protocol):
    @jsii.member(jsii_name="addAdDependency")
    def add_ad_dependency(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
    ) -> None:
        '''Method to configure the Nodes to part of AD Domain Secret: The secrets manager secret to use must be in format: '{Domain: <domain.name>, UserID: 'Admin', Password: ''}' (From cdk-skylight.AwsManagedMicrosoftAd Object).

        :param ad_parameters_store: -
        '''
        ...

    @jsii.member(jsii_name="addEKSDependency")
    def add_eks_dependency(self, eks_cluster: aws_cdk.aws_eks.Cluster) -> None:
        '''Method to add the nodes to specific Cluster.

        :param eks_cluster: -
        '''
        ...

    @jsii.member(jsii_name="addLocalCredFile")
    def add_local_cred_file(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
        ad_group_name: builtins.str,
        account_name: builtins.str,
    ) -> None:
        '''Method to add support for LocalCredFile .

        :param ad_parameters_store: -
        :param ad_group_name: -
        :param account_name: -
        '''
        ...

    @jsii.member(jsii_name="addStorageDependency")
    def add_storage_dependency(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
        fsx_parameters_store: _IFSxWindowsParameters_64d66ceb,
        folder_name: builtins.str,
    ) -> None:
        '''Method to configure persistent storage dependency to the hosts by using Global Mapping.

        :param ad_parameters_store: -
        :param fsx_parameters_store: -
        :param folder_name: -
        '''
        ...

    @jsii.member(jsii_name="addUserData")
    def add_user_data(self, *commands: builtins.str) -> None:
        '''Method to add userData to the nodes.

        :param commands: -
        '''
        ...


class _IRuntimeNodesProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.compute.IRuntimeNodes"

    @jsii.member(jsii_name="addAdDependency")
    def add_ad_dependency(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
    ) -> None:
        '''Method to configure the Nodes to part of AD Domain Secret: The secrets manager secret to use must be in format: '{Domain: <domain.name>, UserID: 'Admin', Password: ''}' (From cdk-skylight.AwsManagedMicrosoftAd Object).

        :param ad_parameters_store: -
        '''
        return typing.cast(None, jsii.invoke(self, "addAdDependency", [ad_parameters_store]))

    @jsii.member(jsii_name="addEKSDependency")
    def add_eks_dependency(self, eks_cluster: aws_cdk.aws_eks.Cluster) -> None:
        '''Method to add the nodes to specific Cluster.

        :param eks_cluster: -
        '''
        return typing.cast(None, jsii.invoke(self, "addEKSDependency", [eks_cluster]))

    @jsii.member(jsii_name="addLocalCredFile")
    def add_local_cred_file(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
        ad_group_name: builtins.str,
        account_name: builtins.str,
    ) -> None:
        '''Method to add support for LocalCredFile .

        :param ad_parameters_store: -
        :param ad_group_name: -
        :param account_name: -
        '''
        return typing.cast(None, jsii.invoke(self, "addLocalCredFile", [ad_parameters_store, ad_group_name, account_name]))

    @jsii.member(jsii_name="addStorageDependency")
    def add_storage_dependency(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
        fsx_parameters_store: _IFSxWindowsParameters_64d66ceb,
        folder_name: builtins.str,
    ) -> None:
        '''Method to configure persistent storage dependency to the hosts by using Global Mapping.

        :param ad_parameters_store: -
        :param fsx_parameters_store: -
        :param folder_name: -
        '''
        return typing.cast(None, jsii.invoke(self, "addStorageDependency", [ad_parameters_store, fsx_parameters_store, folder_name]))

    @jsii.member(jsii_name="addUserData")
    def add_user_data(self, *commands: builtins.str) -> None:
        '''Method to add userData to the nodes.

        :param commands: -
        '''
        return typing.cast(None, jsii.invoke(self, "addUserData", [*commands]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRuntimeNodes).__jsii_proxy_class__ = lambda : _IRuntimeNodesProxy


@jsii.interface(jsii_type="cdk-skylight.compute.IWindowsEKSClusterParameters")
class IWindowsEKSClusterParameters(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNamePointer")
    def cluster_name_pointer(self) -> typing.Optional[builtins.str]:
        '''The name of the SSM Object that contains the EKS Cluster name.

        :default: - 'windows-eks-cluster-name'.
        '''
        ...

    @cluster_name_pointer.setter
    def cluster_name_pointer(self, value: typing.Optional[builtins.str]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The SSM namespace to read/write parameters to.

        :default: - 'cdk-skylight/compute/eks'.
        '''
        ...

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IWindowsEKSClusterParametersProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.compute.IWindowsEKSClusterParameters"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="clusterNamePointer")
    def cluster_name_pointer(self) -> typing.Optional[builtins.str]:
        '''The name of the SSM Object that contains the EKS Cluster name.

        :default: - 'windows-eks-cluster-name'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNamePointer"))

    @cluster_name_pointer.setter
    def cluster_name_pointer(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "clusterNamePointer", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The SSM namespace to read/write parameters to.

        :default: - 'cdk-skylight/compute/eks'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "namespace", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWindowsEKSClusterParameters).__jsii_proxy_class__ = lambda : _IWindowsEKSClusterParametersProxy


@jsii.interface(jsii_type="cdk-skylight.compute.IWindowsEKSClusterProps")
class IWindowsEKSClusterProps(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        ...

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eksSsmParameters")
    def eks_ssm_parameters(self) -> typing.Optional[IWindowsEKSClusterParameters]:
        '''The Windows EKS Cluster parameters.

        :default: - 'No default'.
        '''
        ...

    @eks_ssm_parameters.setter
    def eks_ssm_parameters(
        self,
        value: typing.Optional[IWindowsEKSClusterParameters],
    ) -> None:
        ...


class _IWindowsEKSClusterPropsProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.compute.IWindowsEKSClusterProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        jsii.set(self, "vpc", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eksSsmParameters")
    def eks_ssm_parameters(self) -> typing.Optional[IWindowsEKSClusterParameters]:
        '''The Windows EKS Cluster parameters.

        :default: - 'No default'.
        '''
        return typing.cast(typing.Optional[IWindowsEKSClusterParameters], jsii.get(self, "eksSsmParameters"))

    @eks_ssm_parameters.setter
    def eks_ssm_parameters(
        self,
        value: typing.Optional[IWindowsEKSClusterParameters],
    ) -> None:
        jsii.set(self, "eksSsmParameters", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWindowsEKSClusterProps).__jsii_proxy_class__ = lambda : _IWindowsEKSClusterPropsProxy


@jsii.interface(jsii_type="cdk-skylight.compute.IWindowsEKSNodesProps")
class IWindowsEKSNodesProps(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        ...

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''The instance to use.

        :default: - 'm5.large'.
        '''
        ...

    @instance_type.setter
    def instance_type(
        self,
        value: typing.Optional[aws_cdk.aws_ec2.InstanceType],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The SSM namespace to save parameters to.

        :default: - 'cdk-skylight'.
        '''
        ...

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        ...


class _IWindowsEKSNodesPropsProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.compute.IWindowsEKSNodesProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        jsii.set(self, "vpc", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceType")
    def instance_type(self) -> typing.Optional[aws_cdk.aws_ec2.InstanceType]:
        '''The instance to use.

        :default: - 'm5.large'.
        '''
        return typing.cast(typing.Optional[aws_cdk.aws_ec2.InstanceType], jsii.get(self, "instanceType"))

    @instance_type.setter
    def instance_type(
        self,
        value: typing.Optional[aws_cdk.aws_ec2.InstanceType],
    ) -> None:
        jsii.set(self, "instanceType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The SSM namespace to save parameters to.

        :default: - 'cdk-skylight'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "namespace", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IWindowsEKSNodesProps).__jsii_proxy_class__ = lambda : _IWindowsEKSNodesPropsProxy


class WindowsEKSCluster(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-skylight.compute.WindowsEKSCluster",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: IWindowsEKSClusterProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eksCluster")
    def eks_cluster(self) -> aws_cdk.aws_eks.Cluster:
        return typing.cast(aws_cdk.aws_eks.Cluster, jsii.get(self, "eksCluster"))


@jsii.implements(IRuntimeNodes)
class WindowsEKSNodes(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-skylight.compute.WindowsEKSNodes",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: IWindowsEKSNodesProps,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addAdDependency")
    def add_ad_dependency(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
    ) -> None:
        '''Method to configure the Nodes to part of AD Domain Secret: The secrets manager secret to use must be in format: '{Domain: <domain.name>, UserID: 'Admin', Password: ''}' (From cdk-skylight.AwsManagedMicrosoftAd Object).

        :param ad_parameters_store: -
        '''
        return typing.cast(None, jsii.invoke(self, "addAdDependency", [ad_parameters_store]))

    @jsii.member(jsii_name="addEKSDependency")
    def add_eks_dependency(self, eks_cluster: aws_cdk.aws_eks.Cluster) -> None:
        '''Method to add the nodes to specific Cluster.

        :param eks_cluster: -
        '''
        return typing.cast(None, jsii.invoke(self, "addEKSDependency", [eks_cluster]))

    @jsii.member(jsii_name="addLocalCredFile")
    def add_local_cred_file(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
        ad_group_name: builtins.str,
        account_name: builtins.str,
    ) -> None:
        '''Method to add support for LocalCredFile .

        :param ad_parameters_store: -
        :param ad_group_name: -
        :param account_name: -
        '''
        return typing.cast(None, jsii.invoke(self, "addLocalCredFile", [ad_parameters_store, ad_group_name, account_name]))

    @jsii.member(jsii_name="addStorageDependency")
    def add_storage_dependency(
        self,
        ad_parameters_store: _IAwsManagedMicrosoftAdParameters_42a8ccd6,
        fsx_parameters_store: _IFSxWindowsParameters_64d66ceb,
        folder_name: builtins.str,
    ) -> None:
        '''Method to configure persistent storage dependency to the hosts by using Global Mapping.

        :param ad_parameters_store: -
        :param fsx_parameters_store: -
        :param folder_name: -
        '''
        return typing.cast(None, jsii.invoke(self, "addStorageDependency", [ad_parameters_store, fsx_parameters_store, folder_name]))

    @jsii.member(jsii_name="addUserData")
    def add_user_data(self, *commands: builtins.str) -> None:
        '''Method to add userData to the nodes.

        :param commands: -
        '''
        return typing.cast(None, jsii.invoke(self, "addUserData", [*commands]))

    @jsii.member(jsii_name="gMSAWebHookAutoInstall")
    def g_msa_web_hook_auto_install(
        self,
        eks_cluster: aws_cdk.aws_eks.Cluster,
        private_signer_name: builtins.str,
        awsaccountid: builtins.str,
        awsregion: builtins.str,
    ) -> None:
        '''
        :param eks_cluster: -
        :param private_signer_name: -
        :param awsaccountid: -
        :param awsregion: -
        '''
        return typing.cast(None, jsii.invoke(self, "gMSAWebHookAutoInstall", [eks_cluster, private_signer_name, awsaccountid, awsregion]))

    @jsii.member(jsii_name="runPowerShellSSMDocument")
    def run_power_shell_ssm_document(
        self,
        name: builtins.str,
        commands: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: -
        :param commands: -
        '''
        return typing.cast(None, jsii.invoke(self, "runPowerShellSSMDocument", [name, commands]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="asg")
    def asg(self) -> aws_cdk.aws_autoscaling.AutoScalingGroup:
        return typing.cast(aws_cdk.aws_autoscaling.AutoScalingGroup, jsii.get(self, "asg"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="asgResource")
    def asg_resource(self) -> aws_cdk.aws_autoscaling.CfnAutoScalingGroup:
        return typing.cast(aws_cdk.aws_autoscaling.CfnAutoScalingGroup, jsii.get(self, "asgResource"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nodesSg")
    def nodes_sg(self) -> aws_cdk.aws_ec2.SecurityGroup:
        return typing.cast(aws_cdk.aws_ec2.SecurityGroup, jsii.get(self, "nodesSg"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="windowsWorkersRole")
    def windows_workers_role(self) -> aws_cdk.aws_iam.Role:
        return typing.cast(aws_cdk.aws_iam.Role, jsii.get(self, "windowsWorkersRole"))


__all__ = [
    "DomainWindowsNode",
    "IDomainWindowsNodeProps",
    "IRuntimeNodes",
    "IWindowsEKSClusterParameters",
    "IWindowsEKSClusterProps",
    "IWindowsEKSNodesProps",
    "WindowsEKSCluster",
    "WindowsEKSNodes",
]

publication.publish()
