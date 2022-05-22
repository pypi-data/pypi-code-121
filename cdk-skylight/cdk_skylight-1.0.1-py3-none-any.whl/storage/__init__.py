import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_fsx
import aws_cdk.aws_secretsmanager
import constructs
from ..compute import DomainWindowsNode as _DomainWindowsNode_bbfd2a18


class FSxWindows(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-skylight.storage.FSxWindows",
):
    '''A FSxWindows represents an integration pattern of Amazon FSx and Managed AD in a specific VPC.

    The Construct creates Amazon FSx for Windows
    The construct also creates (optionally) t3.nano machine that is part of the domain that can be used to run admin-tasks (such as createFolder)

    The createFolder() method creates an SMB Folder in the FSx filesystem, using the domain admin user.
    Please note: When calling createFolder() API, a Lambda will be created to start the worker machine (Using AWS-SDK),
    then each command will be scheduled with State Manager, and the instance will be shut down after complete .
    '''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        props: "IFSxWindowsProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="createFolder")
    def create_folder(
        self,
        worker: _DomainWindowsNode_bbfd2a18,
        folder_name: builtins.str,
        secret_name: aws_cdk.aws_secretsmanager.ISecret,
    ) -> None:
        '''
        :param worker: -
        :param folder_name: -
        :param secret_name: -
        '''
        return typing.cast(None, jsii.invoke(self, "createFolder", [worker, folder_name, secret_name]))

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
    @jsii.member(jsii_name="fsxObject")
    def fsx_object(self) -> aws_cdk.aws_fsx.CfnFileSystem:
        return typing.cast(aws_cdk.aws_fsx.CfnFileSystem, jsii.get(self, "fsxObject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="props")
    def props(self) -> "IFSxWindowsProps":
        return typing.cast("IFSxWindowsProps", jsii.get(self, "props"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmParameters")
    def ssm_parameters(self) -> "IFSxWindowsParameters":
        return typing.cast("IFSxWindowsParameters", jsii.get(self, "ssmParameters"))


@jsii.interface(jsii_type="cdk-skylight.storage.IFSxWindowsParameters")
class IFSxWindowsParameters(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsEndpoint")
    def dns_endpoint(self) -> typing.Optional[builtins.str]:
        '''The name of the parameter to save the FSxEndpoint DNS Endpoint.

        :default: - 'FSxEndpoint-DNS'.
        '''
        ...

    @dns_endpoint.setter
    def dns_endpoint(self, value: typing.Optional[builtins.str]) -> None:
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


class _IFSxWindowsParametersProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.storage.IFSxWindowsParameters"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsEndpoint")
    def dns_endpoint(self) -> typing.Optional[builtins.str]:
        '''The name of the parameter to save the FSxEndpoint DNS Endpoint.

        :default: - 'FSxEndpoint-DNS'.
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsEndpoint"))

    @dns_endpoint.setter
    def dns_endpoint(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "dnsEndpoint", value)

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

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFSxWindowsParameters).__jsii_proxy_class__ = lambda : _IFSxWindowsParametersProxy


@jsii.interface(jsii_type="cdk-skylight.storage.IFSxWindowsProps")
class IFSxWindowsProps(typing_extensions.Protocol):
    '''The properties for the PersistentStorage class.'''

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        ...

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use, must have private subnets.'''
        ...

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemInPrivateSubnet")
    def file_system_in_private_subnet(self) -> typing.Optional[builtins.bool]:
        '''Deploy the Amazon FSx file system in private subnet or public subnet See: https://docs.aws.amazon.com/fsx/latest/WindowsGuide/high-availability-multiAZ.html.

        :default: - true.
        '''
        ...

    @file_system_in_private_subnet.setter
    def file_system_in_private_subnet(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemSize")
    def file_system_size(self) -> typing.Optional[jsii.Number]:
        '''The Filesystem size in GB.

        :default:

        -
        200.
        '''
        ...

    @file_system_size.setter
    def file_system_size(self, value: typing.Optional[jsii.Number]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAZ")
    def multi_az(self) -> typing.Optional[builtins.bool]:
        '''Choosing Single-AZ or Multi-AZ file system deployment See: https://docs.aws.amazon.com/fsx/latest/WindowsGuide/high-availability-multiAZ.html.

        :default: - true.
        '''
        ...

    @multi_az.setter
    def multi_az(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmParameters")
    def ssm_parameters(self) -> typing.Optional[IFSxWindowsParameters]:
        ...

    @ssm_parameters.setter
    def ssm_parameters(self, value: typing.Optional[IFSxWindowsParameters]) -> None:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throughputMbps")
    def throughput_mbps(self) -> typing.Optional[jsii.Number]:
        '''The Filesystem throughput in MBps.

        :default:

        -
        128.
        '''
        ...

    @throughput_mbps.setter
    def throughput_mbps(self, value: typing.Optional[jsii.Number]) -> None:
        ...


class _IFSxWindowsPropsProxy:
    '''The properties for the PersistentStorage class.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-skylight.storage.IFSxWindowsProps"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="directoryId")
    def directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directoryId"))

    @directory_id.setter
    def directory_id(self, value: builtins.str) -> None:
        jsii.set(self, "directoryId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpc")
    def vpc(self) -> aws_cdk.aws_ec2.IVpc:
        '''The VPC to use, must have private subnets.'''
        return typing.cast(aws_cdk.aws_ec2.IVpc, jsii.get(self, "vpc"))

    @vpc.setter
    def vpc(self, value: aws_cdk.aws_ec2.IVpc) -> None:
        jsii.set(self, "vpc", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemInPrivateSubnet")
    def file_system_in_private_subnet(self) -> typing.Optional[builtins.bool]:
        '''Deploy the Amazon FSx file system in private subnet or public subnet See: https://docs.aws.amazon.com/fsx/latest/WindowsGuide/high-availability-multiAZ.html.

        :default: - true.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "fileSystemInPrivateSubnet"))

    @file_system_in_private_subnet.setter
    def file_system_in_private_subnet(
        self,
        value: typing.Optional[builtins.bool],
    ) -> None:
        jsii.set(self, "fileSystemInPrivateSubnet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fileSystemSize")
    def file_system_size(self) -> typing.Optional[jsii.Number]:
        '''The Filesystem size in GB.

        :default:

        -
        200.
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fileSystemSize"))

    @file_system_size.setter
    def file_system_size(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "fileSystemSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiAZ")
    def multi_az(self) -> typing.Optional[builtins.bool]:
        '''Choosing Single-AZ or Multi-AZ file system deployment See: https://docs.aws.amazon.com/fsx/latest/WindowsGuide/high-availability-multiAZ.html.

        :default: - true.
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "multiAZ"))

    @multi_az.setter
    def multi_az(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "multiAZ", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ssmParameters")
    def ssm_parameters(self) -> typing.Optional[IFSxWindowsParameters]:
        return typing.cast(typing.Optional[IFSxWindowsParameters], jsii.get(self, "ssmParameters"))

    @ssm_parameters.setter
    def ssm_parameters(self, value: typing.Optional[IFSxWindowsParameters]) -> None:
        jsii.set(self, "ssmParameters", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="throughputMbps")
    def throughput_mbps(self) -> typing.Optional[jsii.Number]:
        '''The Filesystem throughput in MBps.

        :default:

        -
        128.
        '''
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "throughputMbps"))

    @throughput_mbps.setter
    def throughput_mbps(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "throughputMbps", value)

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFSxWindowsProps).__jsii_proxy_class__ = lambda : _IFSxWindowsPropsProxy


__all__ = [
    "FSxWindows",
    "IFSxWindowsParameters",
    "IFSxWindowsProps",
]

publication.publish()
