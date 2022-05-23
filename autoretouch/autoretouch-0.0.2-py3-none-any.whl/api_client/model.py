import dataclasses
from datetime import datetime
from typing import List, Dict, Optional, Union
from uuid import UUID
import inspect
from dataclasses import dataclass


@dataclass
class BaseModel:
    @classmethod
    def from_dict(cls, dct: Dict):
        """method to instantiate a dataclass without TypeError on extra arguments"""
        params = inspect.signature(cls).parameters
        return cls(**{k: v for k, v in dct.items() if k in params})

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)

    @staticmethod
    def to_uuid(value):
        return value if isinstance(value, UUID) else UUID(value)


@dataclass
class ApiConfig:
    BASE_API_URL: str
    BASE_API_URL_CURRENT: str
    CLIENT_ID: str
    SCOPE: str
    AUDIENCE: str
    AUTH_DOMAIN: str


@dataclass
class DeviceCodeResponse(BaseModel):
    device_code: str
    user_code: str
    verification_uri_complete: str
    expires_in: int
    interval: int


@dataclass
class Credentials:
    access_token: str
    refresh_token: str
    scope: str
    expires_in: int
    token_type: str
    expires_at: Optional[int] = None

    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.expires_in + int(datetime.utcnow().timestamp())


@dataclass
class Page:
    entries: List
    total: int


@dataclass
class Organization(BaseModel):
    id: Union[str, UUID]
    version: Union[str, UUID]
    name: str
    members: List

    def __post_init__(self):
        self.id = self.to_uuid(self.id)
        self.version = self.to_uuid(self.version)


@dataclass
class Workflow(BaseModel):
    id: Union[str, UUID]
    version: Union[str, UUID]
    name: str
    date: str
    author: Dict
    workflowComponents: List
    executionPrice: int

    def __post_init__(self):
        self.id = self.to_uuid(self.id)
        self.version = self.to_uuid(self.version)


@dataclass
class WorkflowExecution(BaseModel):
    id: Union[str, UUID]
    workflow: Union[str, UUID]
    workflowVersion: Union[str, UUID]
    workflowName: str
    organizationId: Union[str, UUID]
    status: str
    userId: str
    createdAt: str
    startedAt: Optional[str]
    finishedAt: Optional[str]
    inputFileName: str
    inputContentHash: str
    resultContentHash: Optional[str]
    resultContentType: Optional[str]
    resultFileName: Optional[str]
    resultPath: Optional[str]
    labels: Dict[str, str]
    chargedCredits: int

    def __post_init__(self):
        for attr in ["id", "workflow", "workflowVersion", "organizationId"]:
            setattr(self, attr, self.to_uuid(getattr(self, attr)))
