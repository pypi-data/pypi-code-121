import uuid
import datetime
from typing import List, Optional
from pydantic import BaseModel, BaseSettings, conlist, SecretStr

class ApprovalNoGroup(BaseModel):
    id: uuid.UUID
    user_email: str  
    approval_timestamp: datetime.datetime = None
    declined_timestamp: datetime.datetime = None
    # secret: SecretStr 

    class Config:
        orm_mode = True

class Approval(ApprovalNoGroup):
    group: 'ApprovalGroupNoUserDetails'

class ApprovalGroupCreate(BaseModel):
    name: str  
    users: conlist(str,min_items=1)
    count: int = 1
    class Config:
        orm_mode = True

class ApprovalGroupNoRequest(BaseModel):
    id: uuid.UUID
    name: str  
    users: conlist(ApprovalNoGroup,min_items=1)
    count: int = 1
    approval_timestamp: datetime.datetime = None

    class Config:
        orm_mode = True

class ApprovalGroupNoUserDetails(ApprovalGroupNoRequest):
    users: conlist(str,min_items=1)
    request: 'ApprovalRequest'

class ApprovalGroup(ApprovalGroupNoRequest):
    request: 'ApprovalRequestNoGroupDetails'

class ApprovalRequestCreate(BaseModel):
    name: str
    repo: str
    build: int 
    stage: int 
    step: int 
    created_by: Optional[str]
    groups: conlist(ApprovalGroupCreate,min_items=1)
    
class ApprovalRequest(ApprovalRequestCreate):
    id: uuid.UUID
    approval_timestamp: datetime.datetime = None
    declined_timestamp: datetime.datetime = None
    created_at: datetime.datetime 
    author_avatar: Optional[str] = None
    groups: conlist(ApprovalGroupNoRequest,min_items=1)
    build_href: Optional[str]
    
    class Config:
        orm_mode = True

class ApprovalRequestNoGroupDetails(ApprovalRequest):
    groups: conlist(str,min_items=1)


class ApprovalResult(BaseModel):
    build: int
    request: ApprovalRequest
    created_at: datetime.datetime
    approved: bool

Approval.update_forward_refs()
ApprovalGroup.update_forward_refs()
ApprovalGroupNoUserDetails.update_forward_refs()
