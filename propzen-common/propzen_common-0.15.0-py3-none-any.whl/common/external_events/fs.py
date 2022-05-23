from uuid import UUID
from dataclasses import dataclass
from propzen.common.service_layer.externalbus import ExternalEvent


@dataclass
class ProfilePictureUploaded(ExternalEvent):
    account_id: UUID
    filename: str
