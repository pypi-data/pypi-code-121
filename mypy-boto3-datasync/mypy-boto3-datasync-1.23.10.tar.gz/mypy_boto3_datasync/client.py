"""
Type annotations for datasync service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_datasync.client import DataSyncClient

    session = Session()
    client: DataSyncClient = session.client("datasync")
    ```
"""
import sys
from typing import IO, Any, Dict, Mapping, Sequence, Type, Union, overload

from botocore.client import BaseClient, ClientMeta
from botocore.response import StreamingBody

from .literals import (
    EfsInTransitEncryptionType,
    HdfsAuthenticationTypeType,
    ObjectStorageServerProtocolType,
    S3StorageClassType,
)
from .paginator import (
    ListAgentsPaginator,
    ListLocationsPaginator,
    ListTagsForResourcePaginator,
    ListTaskExecutionsPaginator,
    ListTasksPaginator,
)
from .type_defs import (
    CreateAgentResponseTypeDef,
    CreateLocationEfsResponseTypeDef,
    CreateLocationFsxLustreResponseTypeDef,
    CreateLocationFsxOpenZfsResponseTypeDef,
    CreateLocationFsxWindowsResponseTypeDef,
    CreateLocationHdfsResponseTypeDef,
    CreateLocationNfsResponseTypeDef,
    CreateLocationObjectStorageResponseTypeDef,
    CreateLocationS3ResponseTypeDef,
    CreateLocationSmbResponseTypeDef,
    CreateTaskResponseTypeDef,
    DescribeAgentResponseTypeDef,
    DescribeLocationEfsResponseTypeDef,
    DescribeLocationFsxLustreResponseTypeDef,
    DescribeLocationFsxOpenZfsResponseTypeDef,
    DescribeLocationFsxWindowsResponseTypeDef,
    DescribeLocationHdfsResponseTypeDef,
    DescribeLocationNfsResponseTypeDef,
    DescribeLocationObjectStorageResponseTypeDef,
    DescribeLocationS3ResponseTypeDef,
    DescribeLocationSmbResponseTypeDef,
    DescribeTaskExecutionResponseTypeDef,
    DescribeTaskResponseTypeDef,
    Ec2ConfigTypeDef,
    FilterRuleTypeDef,
    FsxProtocolTypeDef,
    HdfsNameNodeTypeDef,
    ListAgentsResponseTypeDef,
    ListLocationsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListTaskExecutionsResponseTypeDef,
    ListTasksResponseTypeDef,
    LocationFilterTypeDef,
    NfsMountOptionsTypeDef,
    OnPremConfigTypeDef,
    OptionsTypeDef,
    QopConfigurationTypeDef,
    S3ConfigTypeDef,
    SmbMountOptionsTypeDef,
    StartTaskExecutionResponseTypeDef,
    TagListEntryTypeDef,
    TaskFilterTypeDef,
    TaskScheduleTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("DataSyncClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    ClientError: Type[BotocoreClientError]
    InternalException: Type[BotocoreClientError]
    InvalidRequestException: Type[BotocoreClientError]


class DataSyncClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        DataSyncClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#can_paginate)
        """

    def cancel_task_execution(self, *, TaskExecutionArn: str) -> Dict[str, Any]:
        """
        Cancels execution of a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.cancel_task_execution)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#cancel_task_execution)
        """

    def create_agent(
        self,
        *,
        ActivationKey: str,
        AgentName: str = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...,
        VpcEndpointId: str = ...,
        SubnetArns: Sequence[str] = ...,
        SecurityGroupArns: Sequence[str] = ...
    ) -> CreateAgentResponseTypeDef:
        """
        Activates an DataSync agent that you have deployed on your host.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_agent)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_agent)
        """

    def create_location_efs(
        self,
        *,
        EfsFilesystemArn: str,
        Ec2Config: Ec2ConfigTypeDef,
        Subdirectory: str = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...,
        AccessPointArn: str = ...,
        FileSystemAccessRoleArn: str = ...,
        InTransitEncryption: EfsInTransitEncryptionType = ...
    ) -> CreateLocationEfsResponseTypeDef:
        """
        Creates an endpoint for an Amazon EFS file system that DataSync can access for a
        transfer.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_efs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_efs)
        """

    def create_location_fsx_lustre(
        self,
        *,
        FsxFilesystemArn: str,
        SecurityGroupArns: Sequence[str],
        Subdirectory: str = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationFsxLustreResponseTypeDef:
        """
        Creates an endpoint for an Amazon FSx for Lustre file system.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_fsx_lustre)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_fsx_lustre)
        """

    def create_location_fsx_open_zfs(
        self,
        *,
        FsxFilesystemArn: str,
        Protocol: FsxProtocolTypeDef,
        SecurityGroupArns: Sequence[str],
        Subdirectory: str = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationFsxOpenZfsResponseTypeDef:
        """
        Creates an endpoint for an Amazon FSx for OpenZFS file system.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_fsx_open_zfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_fsx_open_zfs)
        """

    def create_location_fsx_windows(
        self,
        *,
        FsxFilesystemArn: str,
        SecurityGroupArns: Sequence[str],
        User: str,
        Password: str,
        Subdirectory: str = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...,
        Domain: str = ...
    ) -> CreateLocationFsxWindowsResponseTypeDef:
        """
        Creates an endpoint for an Amazon FSx for Windows File Server file system.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_fsx_windows)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_fsx_windows)
        """

    def create_location_hdfs(
        self,
        *,
        NameNodes: Sequence[HdfsNameNodeTypeDef],
        AuthenticationType: HdfsAuthenticationTypeType,
        AgentArns: Sequence[str],
        Subdirectory: str = ...,
        BlockSize: int = ...,
        ReplicationFactor: int = ...,
        KmsKeyProviderUri: str = ...,
        QopConfiguration: QopConfigurationTypeDef = ...,
        SimpleUser: str = ...,
        KerberosPrincipal: str = ...,
        KerberosKeytab: Union[str, bytes, IO[Any], StreamingBody] = ...,
        KerberosKrb5Conf: Union[str, bytes, IO[Any], StreamingBody] = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationHdfsResponseTypeDef:
        """
        Creates an endpoint for a Hadoop Distributed File System (HDFS).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_hdfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_hdfs)
        """

    def create_location_nfs(
        self,
        *,
        Subdirectory: str,
        ServerHostname: str,
        OnPremConfig: OnPremConfigTypeDef,
        MountOptions: NfsMountOptionsTypeDef = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationNfsResponseTypeDef:
        """
        Defines a file system on a Network File System (NFS) server that can be read
        from or written to.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_nfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_nfs)
        """

    def create_location_object_storage(
        self,
        *,
        ServerHostname: str,
        BucketName: str,
        AgentArns: Sequence[str],
        ServerPort: int = ...,
        ServerProtocol: ObjectStorageServerProtocolType = ...,
        Subdirectory: str = ...,
        AccessKey: str = ...,
        SecretKey: str = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationObjectStorageResponseTypeDef:
        """
        Creates an endpoint for a self-managed object storage bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_object_storage)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_object_storage)
        """

    def create_location_s3(
        self,
        *,
        S3BucketArn: str,
        S3Config: S3ConfigTypeDef,
        Subdirectory: str = ...,
        S3StorageClass: S3StorageClassType = ...,
        AgentArns: Sequence[str] = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationS3ResponseTypeDef:
        """
        Creates an endpoint for an Amazon S3 bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_s3)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_s3)
        """

    def create_location_smb(
        self,
        *,
        Subdirectory: str,
        ServerHostname: str,
        User: str,
        Password: str,
        AgentArns: Sequence[str],
        Domain: str = ...,
        MountOptions: SmbMountOptionsTypeDef = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...
    ) -> CreateLocationSmbResponseTypeDef:
        """
        Defines a file system on a Server Message Block (SMB) server that can be read
        from or written to.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_location_smb)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_location_smb)
        """

    def create_task(
        self,
        *,
        SourceLocationArn: str,
        DestinationLocationArn: str,
        CloudWatchLogGroupArn: str = ...,
        Name: str = ...,
        Options: OptionsTypeDef = ...,
        Excludes: Sequence[FilterRuleTypeDef] = ...,
        Schedule: TaskScheduleTypeDef = ...,
        Tags: Sequence[TagListEntryTypeDef] = ...,
        Includes: Sequence[FilterRuleTypeDef] = ...
    ) -> CreateTaskResponseTypeDef:
        """
        Creates a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.create_task)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#create_task)
        """

    def delete_agent(self, *, AgentArn: str) -> Dict[str, Any]:
        """
        Deletes an agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.delete_agent)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#delete_agent)
        """

    def delete_location(self, *, LocationArn: str) -> Dict[str, Any]:
        """
        Deletes the configuration of a location used by DataSync.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.delete_location)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#delete_location)
        """

    def delete_task(self, *, TaskArn: str) -> Dict[str, Any]:
        """
        Deletes a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.delete_task)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#delete_task)
        """

    def describe_agent(self, *, AgentArn: str) -> DescribeAgentResponseTypeDef:
        """
        Returns metadata such as the name, the network interfaces, and the status (that
        is, whether the agent is running or not) for an agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_agent)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_agent)
        """

    def describe_location_efs(self, *, LocationArn: str) -> DescribeLocationEfsResponseTypeDef:
        """
        Returns metadata about your DataSync location for an Amazon EFS file system.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_efs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_efs)
        """

    def describe_location_fsx_lustre(
        self, *, LocationArn: str
    ) -> DescribeLocationFsxLustreResponseTypeDef:
        """
        Returns metadata about an Amazon FSx for Lustre location, such as information
        about its path.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_fsx_lustre)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_fsx_lustre)
        """

    def describe_location_fsx_open_zfs(
        self, *, LocationArn: str
    ) -> DescribeLocationFsxOpenZfsResponseTypeDef:
        """
        Returns metadata about an Amazon FSx for OpenZFS location, such as information
        about its path.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_fsx_open_zfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_fsx_open_zfs)
        """

    def describe_location_fsx_windows(
        self, *, LocationArn: str
    ) -> DescribeLocationFsxWindowsResponseTypeDef:
        """
        Returns metadata about an Amazon FSx for Windows File Server location, such as
        information about its path.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_fsx_windows)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_fsx_windows)
        """

    def describe_location_hdfs(self, *, LocationArn: str) -> DescribeLocationHdfsResponseTypeDef:
        """
        Returns metadata, such as the authentication information about the Hadoop
        Distributed File System (HDFS) location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_hdfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_hdfs)
        """

    def describe_location_nfs(self, *, LocationArn: str) -> DescribeLocationNfsResponseTypeDef:
        """
        Returns metadata, such as the path information, about an NFS location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_nfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_nfs)
        """

    def describe_location_object_storage(
        self, *, LocationArn: str
    ) -> DescribeLocationObjectStorageResponseTypeDef:
        """
        Returns metadata about a self-managed object storage server location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_object_storage)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_object_storage)
        """

    def describe_location_s3(self, *, LocationArn: str) -> DescribeLocationS3ResponseTypeDef:
        """
        Returns metadata, such as bucket name, about an Amazon S3 bucket location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_s3)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_s3)
        """

    def describe_location_smb(self, *, LocationArn: str) -> DescribeLocationSmbResponseTypeDef:
        """
        Returns metadata, such as the path and user information about an SMB location.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_location_smb)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_location_smb)
        """

    def describe_task(self, *, TaskArn: str) -> DescribeTaskResponseTypeDef:
        """
        Returns metadata about a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_task)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_task)
        """

    def describe_task_execution(
        self, *, TaskExecutionArn: str
    ) -> DescribeTaskExecutionResponseTypeDef:
        """
        Returns detailed metadata about a task that is being executed.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.describe_task_execution)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#describe_task_execution)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#generate_presigned_url)
        """

    def list_agents(
        self, *, MaxResults: int = ..., NextToken: str = ...
    ) -> ListAgentsResponseTypeDef:
        """
        Returns a list of agents owned by an Amazon Web Services account in the Amazon
        Web Services Region specified in the request.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.list_agents)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#list_agents)
        """

    def list_locations(
        self,
        *,
        MaxResults: int = ...,
        NextToken: str = ...,
        Filters: Sequence[LocationFilterTypeDef] = ...
    ) -> ListLocationsResponseTypeDef:
        """
        Returns a list of source and destination locations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.list_locations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#list_locations)
        """

    def list_tags_for_resource(
        self, *, ResourceArn: str, MaxResults: int = ..., NextToken: str = ...
    ) -> ListTagsForResourceResponseTypeDef:
        """
        Returns all the tags associated with a specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#list_tags_for_resource)
        """

    def list_task_executions(
        self, *, TaskArn: str = ..., MaxResults: int = ..., NextToken: str = ...
    ) -> ListTaskExecutionsResponseTypeDef:
        """
        Returns a list of executed tasks.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.list_task_executions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#list_task_executions)
        """

    def list_tasks(
        self,
        *,
        MaxResults: int = ...,
        NextToken: str = ...,
        Filters: Sequence[TaskFilterTypeDef] = ...
    ) -> ListTasksResponseTypeDef:
        """
        Returns a list of all the tasks.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.list_tasks)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#list_tasks)
        """

    def start_task_execution(
        self,
        *,
        TaskArn: str,
        OverrideOptions: OptionsTypeDef = ...,
        Includes: Sequence[FilterRuleTypeDef] = ...,
        Excludes: Sequence[FilterRuleTypeDef] = ...
    ) -> StartTaskExecutionResponseTypeDef:
        """
        Starts a specific invocation of a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.start_task_execution)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#start_task_execution)
        """

    def tag_resource(
        self, *, ResourceArn: str, Tags: Sequence[TagListEntryTypeDef]
    ) -> Dict[str, Any]:
        """
        Applies a key-value pair to an Amazon Web Services resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, Keys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes a tag from an Amazon Web Services resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#untag_resource)
        """

    def update_agent(self, *, AgentArn: str, Name: str = ...) -> Dict[str, Any]:
        """
        Updates the name of an agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_agent)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_agent)
        """

    def update_location_hdfs(
        self,
        *,
        LocationArn: str,
        Subdirectory: str = ...,
        NameNodes: Sequence[HdfsNameNodeTypeDef] = ...,
        BlockSize: int = ...,
        ReplicationFactor: int = ...,
        KmsKeyProviderUri: str = ...,
        QopConfiguration: QopConfigurationTypeDef = ...,
        AuthenticationType: HdfsAuthenticationTypeType = ...,
        SimpleUser: str = ...,
        KerberosPrincipal: str = ...,
        KerberosKeytab: Union[str, bytes, IO[Any], StreamingBody] = ...,
        KerberosKrb5Conf: Union[str, bytes, IO[Any], StreamingBody] = ...,
        AgentArns: Sequence[str] = ...
    ) -> Dict[str, Any]:
        """
        Updates some parameters of a previously created location for a Hadoop
        Distributed File System cluster.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_location_hdfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_location_hdfs)
        """

    def update_location_nfs(
        self,
        *,
        LocationArn: str,
        Subdirectory: str = ...,
        OnPremConfig: OnPremConfigTypeDef = ...,
        MountOptions: NfsMountOptionsTypeDef = ...
    ) -> Dict[str, Any]:
        """
        Updates some of the parameters of a previously created location for Network File
        System (NFS) access.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_location_nfs)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_location_nfs)
        """

    def update_location_object_storage(
        self,
        *,
        LocationArn: str,
        ServerPort: int = ...,
        ServerProtocol: ObjectStorageServerProtocolType = ...,
        Subdirectory: str = ...,
        AccessKey: str = ...,
        SecretKey: str = ...,
        AgentArns: Sequence[str] = ...
    ) -> Dict[str, Any]:
        """
        Updates some of the parameters of a previously created location for self-managed
        object storage server access.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_location_object_storage)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_location_object_storage)
        """

    def update_location_smb(
        self,
        *,
        LocationArn: str,
        Subdirectory: str = ...,
        User: str = ...,
        Domain: str = ...,
        Password: str = ...,
        AgentArns: Sequence[str] = ...,
        MountOptions: SmbMountOptionsTypeDef = ...
    ) -> Dict[str, Any]:
        """
        Updates some of the parameters of a previously created location for Server
        Message Block (SMB) file system access.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_location_smb)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_location_smb)
        """

    def update_task(
        self,
        *,
        TaskArn: str,
        Options: OptionsTypeDef = ...,
        Excludes: Sequence[FilterRuleTypeDef] = ...,
        Schedule: TaskScheduleTypeDef = ...,
        Name: str = ...,
        CloudWatchLogGroupArn: str = ...,
        Includes: Sequence[FilterRuleTypeDef] = ...
    ) -> Dict[str, Any]:
        """
        Updates the metadata associated with a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_task)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_task)
        """

    def update_task_execution(
        self, *, TaskExecutionArn: str, Options: OptionsTypeDef
    ) -> Dict[str, Any]:
        """
        Updates execution of a task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.update_task_execution)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#update_task_execution)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_agents"]) -> ListAgentsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_locations"]) -> ListLocationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_tags_for_resource"]
    ) -> ListTagsForResourcePaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_task_executions"]
    ) -> ListTaskExecutionsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_tasks"]) -> ListTasksPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/datasync.html#DataSync.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/client/#get_paginator)
        """
