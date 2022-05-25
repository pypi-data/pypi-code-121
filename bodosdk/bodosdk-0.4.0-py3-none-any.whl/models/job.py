import enum
from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID

import pydantic
from pydantic import Field

from bodosdk.models.base import JobStatus, TaskStatus, CamelCaseBase


class JobClusterDefinition(CamelCaseBase):
    instance_type: str = Field(..., alias='instanceType')
    workers_quantity: int = Field(..., alias='workersQuantity')
    accelerated_networking: bool = Field(..., alias='acceleratedNetworking')
    image_id: str = Field(..., alias='imageId')


class JobCluster(pydantic.BaseModel):
    uuid: Union[str, UUID]


class JobSourceType(enum.Enum):
    GIT = 'GIT'
    S3 = 'S3'
    WORKSPACE = 'WORKSPACE'


class GitRepoSource(CamelCaseBase):
    type: JobSourceType = Field(JobSourceType.GIT, const=True)
    repo_url: str = Field(..., alias='repoUrl')
    reference: Optional[str] = ""
    username: str
    token: str


class S3Source(CamelCaseBase):
    type: JobSourceType = Field(JobSourceType.S3, const=True)
    bucket_path: str = Field(..., alias='bucketPath')


class WorkspaceSource(pydantic.BaseModel):
    type: JobSourceType = Field(JobSourceType.WORKSPACE, const=True)
    path: str


class JobDefinition(CamelCaseBase):
    name: str
    args: str
    source_config: Union[GitRepoSource, S3Source, WorkspaceSource] = Field(..., alias="sourceConfig")
    cluster_object: Union[JobClusterDefinition, JobCluster] = Field(..., alias="clusterObject")
    variables: List[str] = Field(default_factory=list)
    timeout: Optional[int] = 120
    retries: Optional[int] = 0
    retries_delay: Optional[int] = Field(0, alias="retriesDelay")
    retry_on_timeout: Optional[bool] = Field(False, alias="retryOnTimeout")


class JobClusterResponse(CamelCaseBase):
    name: str
    instance_type: str = Field(..., alias="instanceType")
    workers_quantity: int = Field(..., alias="workersQuantity")
    accelerated_networking: bool = Field(..., alias="acceleratedNetworking")
    bodo_version: Optional[str] = Field(None, alias="bodoVersion")
    image_id: str = Field(..., alias="imageId")


class JobResponse(CamelCaseBase):
    uuid: UUID
    name: str
    status: JobStatus
    schedule: datetime
    command: str
    variables: List[str]
    workspace_path: str = Field(..., alias="workspacePath")
    workspace_reference: str = Field(..., alias="workspaceReference")
    cluster: JobClusterResponse


class JobCreateResponse(CamelCaseBase):
    uuid: UUID
    status: JobStatus
    name: str
    args: str
    variables: List[str]
    source_config: Union[GitRepoSource, S3Source, WorkspaceSource] = Field(..., alias="sourceConfig")
    clusterConfig: Union[JobClusterDefinition, JobCluster] = Field(..., alias="clusterObject")
    variables: List[str] = Field(default_factory=list)
    timeout: Optional[int] = 120
    retries: Optional[int] = 0
    retries_delay: Optional[int] = Field(0, alias="retriesDelay")
    retry_on_timeout: Optional[bool] = Field(False, alias="retryOnTimeout")


class JobExecution(CamelCaseBase):
    uuid: UUID
    status: TaskStatus
    logs: str
    modify_date: datetime = Field(..., alias="modifyDate")
    created_at: datetime = Field(..., alias="createdAt")
